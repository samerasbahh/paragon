"""Company text: About us, Vision and Services (English + Arabic).
Edit here, then run build.py.
"""

FOUNDED = 2016

ABOUT = [  # (English, Arabic) paragraphs
    ("Established in 2016, Paragon Engineering is a multidisciplinary contracting company specializing in comprehensive interior fit-out, turnkey solutions, landscape design and execution across residential, commercial, hospitality, healthcare, workplace, and food and beverage sectors.",
     "تأسست باراجون للهندسة عام 2016، وهي شركة مقاولات متعددة التخصصات متخصصة في التجهيزات الداخلية المتكاملة، وحلول تسليم المفتاح، وتصميم وتنفيذ المناظر الطبيعية (اللاندسكيب) في القطاعات السكنية والتجارية والضيافة والرعاية الصحية ومساحات العمل والمطاعم والمقاهي."),
    ("With a strong foundation in engineering and project management, Paragon brings together technical expertise, skilled craftsmanship, and a commitment to quality to deliver spaces that meet the highest standards of functionality, aesthetics, and execution.",
     "بفضل أساس متين في الهندسة وإدارة المشاريع، تجمع باراجون بين الخبرة الفنية والحرفية الماهرة والالتزام بالجودة، لتقدّم مساحات تستوفي أعلى معايير الوظيفة والجمال وجودة التنفيذ."),
    ("Our integrated approach encompasses every stage of project delivery, from technical development and detailed engineering to procurement, construction, finishing, and final handover. Through meticulous planning, effective coordination, and rigorous quality control, we ensure that each project is delivered with precision, efficiency, and attention to detail.",
     "يشمل نهجنا المتكامل جميع مراحل تنفيذ المشروع، من التطوير الفني والهندسة التفصيلية إلى التوريد والتنفيذ والتشطيب والتسليم النهائي. ومن خلال التخطيط الدقيق والتنسيق الفعّال ورقابة الجودة الصارمة، نضمن تنفيذ كل مشروع بدقة وكفاءة واهتمام بالتفاصيل."),
    ("We recognize that every project carries its own vision, complexities, and expectations. Our strength lies in translating these requirements into well-executed environments while maintaining the integrity of the design, optimizing resources, and upholding the highest standards of workmanship.",
     "ندرك أن لكل مشروع رؤيته وتعقيداته وتوقعاته الخاصة. وتكمن قوتنا في تحويل هذه المتطلبات إلى بيئات متقنة التنفيذ، مع الحفاظ على سلامة التصميم، وتحسين استخدام الموارد، والالتزام بأعلى معايير الصنعة."),
    ("Driven by professionalism, accountability, and long-term client relationships, Paragon Engineering is committed to delivering enduring value through reliable execution and consistently high-quality results.",
     "انطلاقاً من المهنية والمسؤولية والعلاقات طويلة الأمد مع عملائنا، تلتزم باراجون للهندسة بتقديم قيمة مستدامة من خلال تنفيذ موثوق ونتائج عالية الجودة باستمرار."),
]

# Delivery stages named in the "integrated approach" paragraph
STAGES = [  # icon, English, Arabic
    ('pen', 'Technical development', 'التطوير الفني'),
    ('ruler', 'Detailed engineering', 'الهندسة التفصيلية'),
    ('clipboard', 'Procurement', 'التوريد'),
    ('hammer', 'Construction', 'التنفيذ'),
    ('brush', 'Finishing', 'التشطيب'),
    ('key', 'Final handover', 'التسليم النهائي'),
]

VISION = [
    ("To be a leading design-build and contracting partner across the MENA region, recognized for engineering excellence, innovative solutions, exceptional quality, and a lasting positive impact on the communities we serve.",
     "أن نكون شريكاً رائداً في التصميم والتنفيذ والمقاولات في منطقة الشرق الأوسط وشمال أفريقيا، معروفاً بالتميّز الهندسي والحلول المبتكرة والجودة الاستثنائية والأثر الإيجابي الدائم في المجتمعات التي نخدمها."),
    ("We aspire to transform our clients’ visions into reality by delivering projects of varying scales and complexities, combining technical expertise, creativity, and meticulous attention to detail. Through experienced engineering teams, effective project management, and adherence to international standards, we are committed to exceeding expectations in quality, safety, cost-efficiency, and timely delivery, while building lasting relationships founded on trust and professional integrity.",
     "نطمح إلى تحويل رؤى عملائنا إلى واقع من خلال تنفيذ مشاريع بمختلف الأحجام ودرجات التعقيد، تجمع بين الخبرة الفنية والإبداع والاهتمام الدقيق بالتفاصيل. ومن خلال فرق هندسية متمرّسة وإدارة فعّالة للمشاريع والالتزام بالمعايير الدولية، نلتزم بتجاوز التوقعات في الجودة والسلامة وكفاءة التكلفة والتسليم في الوقت المحدد، مع بناء علاقات دائمة قائمة على الثقة والنزاهة المهنية."),
    ("Beyond delivering exceptional spaces, we are dedicated to developing the next generation of professionals through mentorship, training, and practical opportunities. By embracing sustainable practices, environmental responsibility, and community engagement, we strive to create lasting value for our clients, our people, and society.",
     "وإلى جانب تقديم مساحات استثنائية، نكرّس جهودنا لتطوير الجيل القادم من المهنيين من خلال الإرشاد والتدريب والفرص العملية. ومن خلال تبنّي الممارسات المستدامة والمسؤولية البيئية والمشاركة المجتمعية، نسعى إلى خلق قيمة دائمة لعملائنا وفريقنا والمجتمع."),
]

# id, photo (project slug, photo no.), icon, title EN/AR, short line EN/AR, full text EN/AR, features [(EN, AR)]
SERVICES = [
    dict(id='design', img=('ramallah-federation-center', '01'), icon='pen',
         title=('Design & Technical Consultancy', 'التصميم والاستشارات الفنية'),
         short=('Architectural, interior and technical design that is refined, buildable and on-brief.', 'تصميم معماري وداخلي وفني راقٍ وقابل للتنفيذ ومتوافق مع أهداف المشروع.'),
         text=('Comprehensive architectural, interior, and technical design services, transforming project requirements into functional, innovative, and aesthetically refined solutions. Our approach integrates creative vision with technical expertise, ensuring design excellence, constructability, and alignment with project objectives.',
               'خدمات متكاملة في التصميم المعماري والداخلي والفني، تحوّل متطلبات المشروع إلى حلول عملية ومبتكرة وراقية جمالياً. يدمج نهجنا الرؤية الإبداعية مع الخبرة الفنية لضمان تميّز التصميم وقابليته للتنفيذ وانسجامه مع أهداف المشروع.'),
         feats=[('Architectural design', 'التصميم المعماري'), ('Interior design', 'التصميم الداخلي'), ('Technical design', 'التصميم الفني'), ('Constructability', 'قابلية التنفيذ')]),
    dict(id='contracting', img=('userpilot-ramallah', '01'), icon='hammer',
         title=('General Contracting, Renovation & Fit-Out Works', 'المقاولات العامة والتجديد والتجهيزات الداخلية'),
         short=('Fit-outs, refurbishment and finishing works delivered with precision and rigorous quality control.', 'تجهيزات داخلية وتجديد وأعمال تشطيب بدقة ورقابة صارمة على الجودة.'),
         text=('Comprehensive contracting services encompassing interior fit-outs, refurbishment, renovation, and finishing works across residential, commercial, hospitality, and specialized developments. We deliver projects through coordinated construction processes, skilled execution, and rigorous quality control, ensuring precision, efficiency, and superior finishing standards.',
               'خدمات مقاولات شاملة تغطي التجهيزات الداخلية والتجديد والترميم وأعمال التشطيب في المشاريع السكنية والتجارية والفندقية والمتخصصة. ننفّذ المشاريع من خلال عمليات إنشاء منسّقة وتنفيذ متقن ورقابة صارمة على الجودة، بما يضمن الدقة والكفاءة وأعلى معايير التشطيب.'),
         feats=[('Interior fit-out', 'التجهيزات الداخلية'), ('Refurbishment & renovation', 'التجديد والترميم'), ('Finishing works', 'أعمال التشطيب'), ('Quality control', 'رقابة الجودة')]),
    dict(id='joinery', img=('sa-apartment', '01'), icon='ruler',
         title=('Bespoke Joinery & Architectural Woodworks', 'النجارة حسب الطلب والأعمال الخشبية المعمارية'),
         short=('Wall cladding, cabinetry, integrated furniture and doors, crafted to measure.', 'تكسيات جدران وخزائن وأثاث مدمج وأبواب مصنوعة حسب المقاس.'),
         text=('Specialized joinery and custom woodwork solutions, including architectural wall cladding, bespoke cabinetry, integrated furniture, doors, and decorative timber elements. From technical detailing and material selection to fabrication coordination and installation, we deliver tailored solutions with precision craftsmanship and exceptional attention to detail.',
               'حلول متخصصة في النجارة والأعمال الخشبية حسب الطلب، تشمل التكسيات الخشبية للجدران والخزائن المصممة خصيصاً والأثاث المدمج والأبواب والعناصر الخشبية الزخرفية. من التفاصيل الفنية واختيار المواد إلى تنسيق التصنيع والتركيب، نقدّم حلولاً مخصّصة بحرفية دقيقة واهتمام استثنائي بالتفاصيل.'),
         feats=[('Wall cladding', 'تكسيات الجدران'), ('Bespoke cabinetry', 'خزائن حسب الطلب'), ('Integrated furniture & doors', 'أثاث مدمج وأبواب'), ('Decorative timber', 'عناصر خشبية زخرفية')]),
    dict(id='landscape', img=('sk-rooftop', '03'), icon='compass',
         title=('Landscape Design & Construction', 'تصميم وتنفيذ المناظر الطبيعية (اللاندسكيب)'),
         short=('Hardscape, softscape, pools, lighting and outdoor living spaces.', 'أعمال صلبة وزراعية وبرك سباحة وإنارة ومساحات معيشة خارجية.'),
         text=('Integrated landscape design and construction services encompassing hardscape, softscape, outdoor living environments, swimming pools, landscape lighting, and external architectural features. Our solutions combine aesthetic vision, functionality, and technical execution to create cohesive, enduring outdoor spaces.',
               'خدمات متكاملة في تصميم وتنفيذ المناظر الطبيعية تشمل الأعمال الصلبة والزراعية ومساحات المعيشة الخارجية وبرك السباحة وإنارة الحدائق والعناصر المعمارية الخارجية. تجمع حلولنا بين الرؤية الجمالية والوظيفة والتنفيذ الفني لخلق مساحات خارجية متناغمة تدوم طويلاً.'),
         feats=[('Hardscape & softscape', 'الأعمال الصلبة والزراعية'), ('Outdoor living', 'مساحات المعيشة الخارجية'), ('Swimming pools', 'برك السباحة'), ('Landscape lighting', 'إنارة الحدائق')]),
    dict(id='project-management', img=('qcom-ramallah', '02'), icon='clipboard',
         title=('Project Management & Delivery', 'إدارة وتنفيذ المشاريع'),
         short=('Planning, budgets, schedules, procurement and handover, all under control.', 'التخطيط والميزانيات والجداول والتوريد والتسليم تحت السيطرة.'),
         text=('Professional project management services covering planning, budgeting, scheduling, procurement coordination, contractor management, quality assurance, and project handover. We ensure effective coordination across all disciplines while maintaining control over project timelines, costs, and execution standards.',
               'خدمات احترافية في إدارة المشاريع تشمل التخطيط وإعداد الميزانيات والجدولة وتنسيق التوريد وإدارة المقاولين وضمان الجودة وتسليم المشروع. نضمن تنسيقاً فعّالاً بين جميع التخصصات مع الحفاظ على السيطرة على الجداول الزمنية والتكاليف ومعايير التنفيذ.'),
         feats=[('Planning & budgeting', 'التخطيط والميزانية'), ('Scheduling & procurement', 'الجدولة والتوريد'), ('Contractor management', 'إدارة المقاولين'), ('Quality assurance & handover', 'ضمان الجودة والتسليم')]),
    dict(id='facilities', img=('hyundai-mopar-visitor-center', '04'), icon='wrench',
         title=('Facilities Management & Maintenance', 'إدارة المرافق والصيانة'),
         short=('Preventive and corrective maintenance that protects your asset.', 'صيانة وقائية وتصحيحية تحافظ على أصولك.'),
         text=('Comprehensive property and facility management solutions focused on operational efficiency, asset preservation, and long-term performance. Our services include preventive and corrective maintenance, technical inspections, refurbishment coordination, and ongoing property upkeep.',
               'حلول شاملة لإدارة العقارات والمرافق تركّز على الكفاءة التشغيلية والحفاظ على الأصول والأداء طويل الأمد. تشمل خدماتنا الصيانة الوقائية والتصحيحية والفحوصات الفنية وتنسيق أعمال التجديد والعناية المستمرة بالعقار.'),
         feats=[('Preventive maintenance', 'صيانة وقائية'), ('Corrective maintenance', 'صيانة تصحيحية'), ('Technical inspections', 'فحوصات فنية'), ('Ongoing upkeep', 'عناية مستمرة')]),
    dict(id='value-engineering', img=('asharq-news-ramallah', '12'), icon='chart',
         title=('Value Engineering & Cost Optimization', 'هندسة القيمة وتحسين التكلفة'),
         short=('Smarter costs, materials and methods, without compromising design or quality.', 'تكاليف ومواد وأساليب أذكى دون المساس بالتصميم أو الجودة.'),
         text=('Strategic value engineering services aimed at optimizing project costs, materials, construction methods, and technical solutions without compromising design intent, functionality, or quality. Through systematic evaluation and practical alternatives, we enhance project efficiency and maximize overall value.',
               'خدمات استراتيجية في هندسة القيمة تهدف إلى تحسين تكاليف المشروع والمواد وأساليب التنفيذ والحلول الفنية دون المساس بفكرة التصميم أو الوظيفة أو الجودة. ومن خلال التقييم المنهجي والبدائل العملية، نعزّز كفاءة المشروع ونحقق أقصى قيمة ممكنة.'),
         feats=[('Cost optimization', 'تحسين التكلفة'), ('Material alternatives', 'بدائل المواد'), ('Construction methods', 'أساليب التنفيذ'), ('Design intent preserved', 'الحفاظ على فكرة التصميم')]),
    dict(id='property-renovation', img=('downtown-studios', '06'), icon='key',
         title=('Property Renovation & Resale Preparation', 'تجديد العقارات وتجهيزها لإعادة البيع'),
         short=('Targeted upgrades that raise market appeal and asset value.', 'تحسينات موجّهة ترفع جاذبية العقار في السوق وقيمته.'),
         text=('Targeted property enhancement and renovation solutions designed to improve market appeal, functionality, and asset value. From strategic upgrades and interior refurbishment to finishing improvements and resale preparation, we help property owners and investors position their assets competitively in the real estate market.',
               'حلول موجّهة لتحسين العقارات وتجديدها بهدف رفع جاذبيتها في السوق وتحسين وظيفتها وزيادة قيمتها. من التحسينات الاستراتيجية والتجديد الداخلي إلى تحسين التشطيبات والتجهيز لإعادة البيع، نساعد مالكي العقارات والمستثمرين على طرح أصولهم بشكل تنافسي في سوق العقارات.'),
         feats=[('Strategic upgrades', 'تحسينات استراتيجية'), ('Interior refurbishment', 'تجديد داخلي'), ('Finishing improvements', 'تحسين التشطيبات'), ('Resale preparation', 'التجهيز لإعادة البيع')]),
]
