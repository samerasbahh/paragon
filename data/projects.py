"""Project list, taken from the Paragon 2024 Fit-out Portfolio.

To add a project: add an entry below, put its photos in assets/projects/<slug>/
(01.webp, 01-t.webp, ...) and list them in data/photos.json, then run build.py.
Dates: (year, month or None). status: 'done' or 'ongoing' (as stated in the portfolio).
"""

SECTORS = [  # key, English, Arabic
    ('hospitality', 'Hospitality', 'الضيافة والثقافة'),
    ('commercial', 'Commercial', 'تجاري'),
    ('healthcare', 'Healthcare', 'الرعاية الصحية'),
    ('workspace', 'Workspace', 'مساحات العمل'),
    ('broadcasting', 'Broadcasting & Acoustics', 'البث والصوتيات'),
    ('residential', 'Residential', 'سكني'),
]

CONTRACTS = {  # key: (English, Arabic)
    'db': ('Design & Build', 'تصميم وتنفيذ'),
    'wm': ('Wood & Metal Works', 'أعمال الخشب والمعادن'),
    'fit': ('Interior Fit-out', 'تجهيز داخلي'),
}

MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MONTHS_AR = ['كانون الثاني', 'شباط', 'آذار', 'نيسان', 'أيار', 'حزيران', 'تموز', 'آب', 'أيلول', 'تشرين الأول', 'تشرين الثاني', 'كانون الأول']

# slug, sector, name EN, name AR, location EN, location AR, contract, (year, month), status, cover photo, extra EN, extra AR
P = [
 ('lemon-restaurant', 'hospitality', 'Lemon Restaurant', 'مطعم ليمون', 'Ramallah', 'رام الله', 'db', (2023, 6), 'done', '03',
  'A bright, plant-filled dining room under a glazed roof for the Ramallah branch of Lemon.', 'صالة طعام مشرقة تملؤها النباتات تحت سقف زجاجي لفرع مطعم ليمون في رام الله.'),
 ('wox-palestine', 'hospitality', 'Wox Palestine', 'ووكس فلسطين', 'Ramallah', 'رام الله', 'db', (2023, 4), 'done', '01', '', ''),
 ('patisserie-yvonne', 'hospitality', 'Patisserie Yvonne', 'باتيسري إيفون', '', '', 'db', (2019, 6), 'done', '01', '', ''),
 ('sobh-w-masa-cafe-bakery', 'hospitality', 'Sobh w Masa Café & Bakery', 'مقهى ومخبز صبح ومسا', '', '', 'db', (2020, 3), 'done', '01', '', ''),
 ('locanda-farah-boutique-hotel', 'hospitality', 'Locanda Farah Boutique Hotel', 'فندق لوكندة فرح البوتيكي', '', '', 'wm', (2023, 9), 'done', '03',
  'Bespoke wood and metal pieces for the rooms of a boutique hotel set in a historic stone building.', 'قطع خشبية ومعدنية مصمّمة خصيصاً لغرف فندق بوتيكي في مبنى حجري تاريخي.'),
 ('locanda-farah-bar', 'hospitality', 'Locanda Farah Bar', 'بار لوكندة فرح', '', '', 'wm', (2023, 9), 'done', '02', '', ''),
 ('ramallah-federation-center', 'hospitality', 'Ramallah Federation Center', 'مركز اتحاد رام الله', 'Ramallah', 'رام الله', 'fit', (2025, None), 'ongoing', '04', '', ''),
 ('edward-said-conservatory-of-music', 'hospitality', 'Edward Said National Conservatory of Music', 'معهد إدوارد سعيد الوطني للموسيقى', '', '', 'wm', (2024, None), 'ongoing', '03', '', ''),
 ('french-german-cultural-center', 'hospitality', 'French German Cultural Center – Institut Français', 'المركز الثقافي الفرنسي الألماني – المعهد الفرنسي', '', '', 'db', (2021, 1), 'done', '03',
  'A library, reading and gathering spaces for the French German Cultural Center.', 'مكتبة ومساحات للقراءة واللقاء في المركز الثقافي الفرنسي الألماني.'),
 ('palestine-cinema-days-festival', 'hospitality', 'Palestine Cinema Days Festival by Filmlab', 'مهرجان أيام فلسطين السينمائية – فيلم لاب', '', '', 'db', (2022, 10), 'done', '03',
  'Festival venue set-ups for the October 2021 and October 2022 editions.', 'تجهيز مواقع المهرجان لدورتي تشرين الأول 2021 وتشرين الأول 2022.'),
 ('hyundai-mopar-visitor-center', 'commercial', 'Hyundai & Mopar Visitor Center', 'مركز زوّار هيونداي وموبار', '', '', 'wm', (2019, 6), 'done', '01', '', ''),
 ('la-vanda-bridal-store', 'commercial', 'La Vanda Bridal Store', 'متجر لافاندا لفساتين الزفاف', '', '', 'db', (2023, 5), 'done', '01',
  'A soft, gallery-like bridal showroom with sculpted display arches.', 'صالة عرض ناعمة لفساتين الزفاف بأقواس عرض منحوتة.'),
 ('al-amani-center', 'commercial', 'Al-Amani Commercial Center', 'أماني سنتر التجاري', '', '', 'db', (2024, 2), 'done', '02', '', ''),
 ('med-dentistry-clinic', 'healthcare', 'MED Dentistry Clinic', 'عيادة MED لطب الأسنان', '', '', 'db', (2024, 9), 'ongoing', '02', '', ''),
 ('dr-adel-asfour-clinic', 'healthcare', 'Dr. Adel Asfour Health & Beauty Clinic', 'عيادة د. عادل عصفور للصحة والتجميل', '', '', 'db', (2023, 12), 'done', '05', '', ''),
 ('dr-salim-basem-clinic', 'healthcare', 'Dr. Salim Basem Clinic Reception', 'استقبال عيادة د. سليم باسم', '', '', 'db', (2024, 9), 'ongoing', '02', '', ''),
 ('userpilot-ramallah', 'workspace', 'Userpilot', 'مكاتب Userpilot', 'Ramallah', 'رام الله', 'db', (2022, 10), 'done', '01',
  'A colourful tech office with collaborative zones, a snack bar and focus areas.', 'مكتب تقني ملوّن بمساحات تعاون وركن للوجبات الخفيفة ومناطق للتركيز.'),
 ('oxfam-ramallah', 'workspace', 'Oxfam International', 'أوكسفام الدولية', 'Ramallah', 'رام الله', 'db', (2023, 5), 'done', '03', '', ''),
 ('bluemina-ramallah', 'workspace', 'Bluemina Citizenship & Residency', 'Bluemina للجنسية والإقامة', 'Ramallah', 'رام الله', 'db', (2023, 5), 'done', '01', '', ''),
 ('qcom-ramallah', 'workspace', 'QCom', 'مكاتب QCom', 'Ramallah', 'رام الله', 'wm', (2024, 7), 'ongoing', '06', '', ''),
 ('asharq-news-ramallah', 'broadcasting', 'Asharq News', 'الشرق للأخبار', 'Ramallah', 'رام الله', 'db', (2021, 3), 'done', '04',
  'Newsroom, studio and editing suites with acoustic treatment for Asharq News.', 'غرفة أخبار واستوديو وغرف مونتاج بمعالجة صوتية لقناة الشرق للأخبار.'),
 ('bloomberg-news-jerusalem', 'broadcasting', 'Bloomberg News', 'بلومبرغ للأخبار', 'Jerusalem', 'القدس', 'db', (2023, 4), 'done', '02', '', ''),
 ('sa-apartment', 'residential', 'S.A. Apartment', 'شقة S.A.', '', '', 'db', (2022, 8), 'done', '02', '', ''),
 ('sd-villa', 'residential', 'S.D. Villa', 'فيلا S.D.', '', '', 'db', (2022, 9), 'done', '04', '', ''),
 ('downtown-studios', 'residential', 'Downtown Studios', 'استوديوهات داون تاون', '', '', 'db', (2021, 6), 'done', '18',
  'Four fully finished studios, each with its own character: Grey Moon, Green Willow, Blue Anchor and Black Forest.', 'أربعة استوديوهات مكتملة التشطيب، لكل منها طابعه الخاص: Grey Moon وGreen Willow وBlue Anchor وBlack Forest.'),
 ('sk-rooftop', 'residential', 'S.K. Rooftop', 'روف S.K.', '', '', 'db', (2024, 4), 'done', '04', '', ''),
 ('mm-apartment', 'residential', 'M.M. Apartment', 'شقة M.M.', '', '', 'wm', (2023, 2), 'done', '03', '', ''),
]

FEATURED = ['sk-rooftop', 'asharq-news-ramallah', 'userpilot-ramallah', 'la-vanda-bridal-store', 'french-german-cultural-center', 'locanda-farah-boutique-hotel']

# Clients from the portfolio's client page. logo: assets/clients/<key>.webp ; projects: slugs above
CLIENTS = [  # key, English, Arabic, [project slugs]
    ('lemon', 'Lemon', 'ليمون', ['lemon-restaurant']),
    ('asharq-news', 'Asharq News', 'الشرق للأخبار', ['asharq-news-ramallah']),
    ('amani-center', 'Amani Center', 'أماني سنتر', ['al-amani-center']),
    ('mopar', 'Mopar', 'موبار', ['hyundai-mopar-visitor-center']),
    ('farah-locanda', 'Farah Locanda', 'لوكندة فرح', ['locanda-farah-boutique-hotel', 'locanda-farah-bar']),
    ('swarovski', 'Swarovski', 'سواروفسكي', []),
    ('goethe-institut', 'Goethe-Institut', 'معهد غوته', ['french-german-cultural-center']),
    ('filmlab-palestine', 'Filmlab Palestine', 'فيلم لاب فلسطين', ['palestine-cinema-days-festival']),
    ('azkadenya', 'Azkadenya', 'أزكادينيا', []),
    ('bluemina', 'Bluemina', 'Bluemina', ['bluemina-ramallah']),
    ('sobh-w-masa', 'Sobh w Masa', 'صبح ومسا', ['sobh-w-masa-cafe-bakery']),
    ('ankars', 'Ankars Suites & Hotel', 'فندق وأجنحة أنكارس', []),
    ('hyundai', 'Hyundai', 'هيونداي', ['hyundai-mopar-visitor-center']),
    ('institut-francais', 'Institut Français', 'المعهد الفرنسي', ['french-german-cultural-center']),
    ('userpilot', 'Userpilot', 'Userpilot', ['userpilot-ramallah']),
    ('the-childrens-place', "The Children's Place", "The Children's Place", []),
    ('bloomberg', 'Bloomberg', 'بلومبرغ', ['bloomberg-news-jerusalem']),
    ('lacasa-mall', 'Lacasa Mall', 'لاكاسا مول', []),
    ('wox', 'Wox', 'ووكس', ['wox-palestine']),
    ('mango', 'Mango', 'مانجو', []),
    ('oxfam', 'Oxfam International', 'أوكسفام الدولية', ['oxfam-ramallah']),
]
