INSERT INTO stock_sectors (id, sector_name) VALUES
(1, '半導體'),
(2, '電腦及週邊'),
(3, '電子零組件'),
(4, '金融業'),
(5, '通信網路'),
(6, '塑膠工業'),
(7, '鋼鐵工業'),
(8, '食品工業'),
(9, '通信設備'),
(10, '電力業'),
(11, '有色金屬'),
(12, '電力設備'),
(13, '食品飲料')
ON DUPLICATE KEY UPDATE sector_name = VALUES(sector_name);

INSERT INTO stock_name_map (id, name_en, name_cn, stock_ticker, sector_id) VALUES
(1, 'Taiwan Semiconductor Manufacturing Co Ltd', '台積電', '2330', 1),
(2, 'Hon Hai Precision Industry Co Ltd', '鴻海', '2317', 2),
(3, 'MediaTek Inc', '聯發科', '2454', 1),
(4, 'Quanta Computer Inc', '廣達', '2382', 2),
(5, 'Delta Electronics Inc', '台達電', '2308', 5),
(6, 'United Microelectronics Corp', '聯電', '2303', 1),
(7, 'Fubon Financial Holdings Co Ltd', '富邦金', '2881', 4),
(8, 'Cathay Financial Holding Co Ltd', '國泰金', '2882', 4),
(9, 'CTBC Financial Holding Co Ltd', '中信金', '2891', 4),
(10, 'Mega Financial Holding Co Ltd', '兆豐金', '2886', 4),
(11, 'ASE Technology Holding Co Ltd', '日月光投控', '3711', 1),
(12, 'Accton Technology Corp', '智邦', '2345', 3),
(13, 'Asustek Computer Inc', '華碩', '2357', 2),
(14, 'Chunghwa Telecom Co Ltd', '中華電', '2412', 5),
(15, 'Nan Ya Plastics Corp', '南亞', '1303', 6),
(16, 'China Steel Corp', '中鋼', '2002', 7),
(17, 'Formosa Plastics Corp', '台塑', '1301', 6),
(18, 'Uni-President Enterprises Corp', '統一', '1216', 8),
(19, 'E.Sun Financial Holding Co Ltd', '玉山金', '2884', 4),
(20, 'First Financial Holding Co Ltd', '第一金', '2892', 4)
ON DUPLICATE KEY UPDATE
name_cn = VALUES(name_cn),
stock_ticker = VALUES(stock_ticker),
sector_id = VALUES(sector_id);
