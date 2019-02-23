import numpy as np
import bz2

class HimawariFormat:

    def __init__(self, filename:str):
        self.filename = filename

    def extract(self):
        self.hsd, raw = self._extract()
        return self.calibration(self.hsd, raw)

    def get_geocoord(self):
        return self.get_lonlat(self.hsd)

    def _extract(self):
        hsd = {}
        f = bz2.open(self.filename, mode='rb')
        hsd['BLOCK_01'] = np.fromstring(f.read(282), dtype=self._BLOCK_01)
        hsd['BLOCK_02'] = np.fromstring(f.read(50), dtype=self._BLOCK_02)
        hsd['BLOCK_03'] = np.fromstring(f.read(127), dtype=self._BLOCK_03)
        self.leap_block(f, 1)
        hsd['BLOCK_05'] = np.fromstring(f.read(35), dtype=self._BLOCK_05)
        if hsd['BLOCK_05']['BandNumber'] <= 6:
            hsd['VisibleBand'] = np.fromstring(f.read(112), dtype=self._VisibleBand)
        else:
            hsd['InfraredBand'] = np.fromstring(f.read(112), dtype=self._InfraredBand)
        self.leap_block(f, 1)
        hsd['BLOCK_07'] = np.fromstring(f.read(47), dtype=self._BLOCK_07)
        self.leap_block(f, 4)
        lines = hsd['BLOCK_02']['NumberOfLines'].item()
        columns = hsd['BLOCK_02']['NumberOfColumns'].item()
        raw = np.ma.masked_greater(np.fromstring(f.read(), dtype='uint16').reshape((lines, columns)), 65530)
        column_west = 0
        column_east = raw.shape[1]
        hsd['ColumnBoundary'] = (column_west, column_east)
        f.close()
        return hsd, raw

    def calibration(self, hsd, raw):
        if hsd['BLOCK_05']['BandNumber'] <= 6:
            return self.vis_calibration(hsd, raw)
        else:
            return self.ir_calibration(hsd, raw)

    def ir_calibration(self, hsd, raw):
        lam = hsd['BLOCK_05']['CentralWaveLength'] * 1e-6
        gain = hsd['BLOCK_05']['Gain']
        const = hsd['BLOCK_05']['Constant']
        c = hsd['InfraredBand']['c']
        k = hsd['InfraredBand']['k']
        h = hsd['InfraredBand']['h']
        c0 = hsd['InfraredBand']['c0']
        c1 = hsd['InfraredBand']['c1']
        c2 = hsd['InfraredBand']['c2']
        const1 = h * c / (k * lam)
        const2 = 2 * h * np.power(c, 2) * np.power(lam, -5)
        I = (gain * raw + const) * 1e6
        EBT = const1 / np.log1p(const2 / I)
        return c0 + c1 * EBT + c2 * np.power(EBT, 2) - 273.15

    def vis_calibration(self, hsd, raw):
        gain = hsd['BLOCK_05']['Gain']
        const = hsd['BLOCK_05']['Constant']
        c = hsd['VisibleBand']['c*']
        return c * gain * raw + c * const

    def get_lonlat(self, hsd):
        #参考JMA提供代码编写
        #Constants
        DEGTORAD = np.pi / 180.
        RADTODEG = 180. / np.pi
        SCLUNIT = np.power(2., -16)
        DIS = hsd['BLOCK_03']['Distance']
        CON = hsd['BLOCK_03']['EarthConst3']
        #Calculation
        lines = np.arange(hsd['BLOCK_07']['FirstLineNumber'], hsd['BLOCK_07']['FirstLineNumber'] + hsd['BLOCK_02']  ['NumberOfLines'])
        columns = np.arange(*hsd['ColumnBoundary'])
        xx, yy = np.meshgrid(columns, lines)
        x = DEGTORAD * (xx - hsd['BLOCK_03']['COFF']) / (SCLUNIT * hsd['BLOCK_03']['CFAC'])
        y = DEGTORAD * (yy - hsd['BLOCK_03']['LOFF']) / (SCLUNIT * hsd['BLOCK_03']['LFAC'])
        Sd = np.sqrt(np.square(DIS * np.cos(x) * np.cos(y)) - (np.square(np.cos(y)) + CON * np.square(np.sin(y)))   * hsd['BLOCK_03']['EarthConstStd'])
        Sn = (DIS * np.cos(x) * np.cos(y) - Sd) / (np.square(np.cos(y)) + CON * np.square(np.sin(y)))
        S1 = DIS - Sn * np.cos(x) * np.cos(y)
        S2 = Sn * np.sin(x) * np.cos(y)
        S3 = -Sn * np.sin(y)
        Sxy = np.sqrt(np.square(S1) + np.square(S2))
        lons = RADTODEG * np.arctan2(S2, S1) + hsd['BLOCK_03']['SubLon']
        lats = np.ma.masked_outside(RADTODEG * np.arctan(CON * S3 / Sxy), -90., 90.)
        return np.ma.masked_invalid(lons), np.ma.masked_invalid(lats)

    def leap_block(self, f, n):
        for i in range(n):
            tmparr = np.fromstring(f.read(3), dtype=self._Header)
            f.seek(tmparr['BlockLength'].item()-3, 1)

    _BLOCK_01 = np.dtype([('HeaderBlockNumber', 'u1'),
                     ('BlockLength', 'u2'),
                     ('TotalNumberOfHeaderBlocks', 'u2'),
                     ('ByteOrder', 'u1'),
                     ('SatelliteName', 'a16'),
                     ('ProcessingCenterName', 'a16'),
                     ('ObservationArea', 'a4'),
                     ('OtherObservationInformation', 'a2'),
                     ('ObservationTimeline', 'u2'),
                     ('ObservationStartTime', 'f8'),
                     ('ObservationEndTime', 'f8'),
                     ('FileCreationTime', 'f8'),
                     ('TotalHeaderLength', 'u4'),
                     ('TotalDataLength', 'u4'),
                     ('QualityFlag1', 'u1'),
                     ('QualityFlag2', 'u1'),
                     ('QualityFlag3', 'u1'),
                     ('QualityFlag4', 'u1'),
                     ('FileFormatVersion', 'a32'),
                     ('FileName', 'a128'),
                     ('Spare', 'a40')])

    _BLOCK_02 = np.dtype([('HeaderBlockNumber', 'u1'),
                     ('BlockLength', 'u2'),
                     ('NumberOfBitsPerPixel', 'u2'),
                     ('NumberOfColumns', 'u2'),
                     ('NumberOfLines', 'u2'),
                     ('CompressionFlag', 'u1'),
                     ('Spare', 'a40')])

    _BLOCK_03 = np.dtype([('HeaderBlockNumber', 'u1'),
                     ('BlockLength', 'u2'),
                     ('SubLon', 'f8'),
                     ('CFAC', 'u4'),
                     ('LFAC', 'u4'),
                     ('COFF', 'f4'),
                     ('LOFF', 'f4'),
                     ('Distance', 'f8'),
                     ('EarthEquatorialRadius', 'f8'),
                     ('EarthPolarRadius', 'f8'),
                     ('EarthConst1', 'f8'),
                     ('EarthConst2', 'f8'),
                     ('EarthConst3', 'f8'),
                     ('EarthConstStd', 'f8'),
                     ('ResamplingTypes', 'u2'),
                     ('ResamplingSize', 'u2'),
                     ('Spare', 'a40')])

    _BLOCK_05 = np.dtype([('HeaderBlockNumber', 'u1'),
                     ('BlockLength', 'u2'),
                     ('BandNumber', 'u2'),
                     ('CentralWaveLength', 'f8'),
                     ('ValidNumberOfBitsPerPixel', 'u2'),
                     ('CountValueOfErrorPixels', 'u2'),
                     ('CountValueOfPixelsOutsideScanArea', 'u2'),
                     ('Gain', 'f8'),
                     ('Constant', 'f8')])

    _InfraredBand = np.dtype([('c0', 'f8'),
                         ('c1', 'f8'),
                         ('c2', 'f8'),
                         ('C0', 'f8'),
                         ('C1', 'f8'),
                         ('C2', 'f8'),
                         ('c', 'f8'),
                         ('h', 'f8'),
                         ('k', 'f8'),
                         ('Spare', 'a40')])

    _VisibleBand = np.dtype([('c*', 'f8'),
                        ('Spare', 'a104')])

    _BLOCK_07 = np.dtype([('HeaderBlockNumber', 'u1'),
                     ('BlockLength', 'u2'),
                     ('TotalNumberOfSegments', 'u1'),
                     ('SegmentSequenceNumber', 'u1'),
                     ('FirstLineNumber', 'u2'),
                     ('Spare', 'a40')])

    _Header = np.dtype([('HeaderBlockNumber', 'u1'),
                ('BlockLength', 'u2')])
