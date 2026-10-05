"""Seed initial data for BAM Studio."""
from app import db
from app.models import (
    Role,
    Permission,
    Service,
    ProcessStep,
    ProjectCategory,
    Project,
    SiteSetting,
    NavigationItem,
    AdminUser,
    Testimonial,
    FAQ,
    TechItem,
    StatItem,
    TeamMember,
    Client,
)


def seed_roles():
    roles_data = [
        ("Super Admin", "Full system access"),
        ("Content Manager", "Projects, services, pages, media"),
        ("HR Manager", "Careers and applications"),
        ("Sales / Support", "Contact and project inquiries"),
    ]
    for name, desc in roles_data:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name, description=desc))
    db.session.commit()


def seed_settings():
    defaults = [
        ("site_name", "BAM Studio", "BAM Studio", "general"),
        ("site_tagline", "Digital Experiences. Engineered.", "डिजिटल अनुभव। ईन्जिनियर गरिएको।", "general"),
        ("email", "hello@bamstudio.com", None, "general"),
        ("phone", "+977-XXXXXXXX", None, "general"),
        ("address", "Nepal", None, "general"),
        ("hero_heading", "WE BUILD DIGITAL EXPERIENCES.", "हामी डिजिटल अनुभव निर्माण गर्छौं।", "homepage"),
        ("hero_desc", "Websites, systems and digital solutions engineered for modern businesses.", "आधुनिक व्यवसायका लागि वेबसाइट, प्रणाली तथा डिजिटल समाधान निर्माण गर्छौं।", "homepage"),
        ("footer_description", "We design and build digital experiences that move businesses forward.", "हामी डिजिटल अनुभव डिजाइन र निर्माण गर्छौं जसले व्यवसायलाई अगाडि बढाउँछ।", "footer"),
        ("copyright", "© BAM Studio — All Rights Reserved.", "© BAM Studio — सर्वाधिकार सुरक्षित।", "footer"),
        ("seo_default_title", "BAM Studio — Digital Experiences. Engineered.", None, "seo"),
        ("seo_default_description", "BAM Studio designs and builds websites, custom software, business systems and digital solutions.", None, "seo"),
    ]
    for key, en, ne, group in defaults:
        if not SiteSetting.query.filter_by(key=key).first():
            db.session.add(SiteSetting(key=key, value_en=en, value_ne=ne, group=group))
    db.session.commit()


def seed_navigation():
    items = [
        ("Work", "काम", "/work", 1),
        ("Services", "सेवाहरू", "/services", 2),
        ("About", "हाम्रो बारे", "/about", 3),
        ("Careers", "क्यारियर", "/careers", 4),
        ("Contact", "सम्पर्क", "/contact", 5),
    ]
    for en, ne, url, order in items:
        if not NavigationItem.query.filter_by(url=url).first():
            db.session.add(
                NavigationItem(label_en=en, label_ne=ne, url=url, display_order=order)
            )
    db.session.commit()


def seed_services():
    services = [
        {
            "number": "01",
            "title_en": "Web Development",
            "title_ne": "वेब डेभलपमेन्ट",
            "description_en": "Modern, responsive and high-performance websites.",
            "description_ne": "आधुनिक, उत्तरदायी र उच्च-प्रदर्शन वेबसाइटहरू।",
            "detail_en": "We design and build production websites that load fast, work on every device, and are easy to maintain.\n\nWhat you get:\n• Responsive layouts for mobile, tablet and desktop\n• Clean HTML/CSS/JavaScript or Flask-powered sites\n• SEO-friendly structure and meta tags\n• Contact forms, CMS content and admin panels when needed\n• Deployment on Vercel, Linux servers or your preferred host\n\nIdeal for businesses, schools, hotels, clubs and organizations that need a reliable online presence.",
            "detail_ne": "हामी छिटो लोड हुने, सबै उपकरणमा चल्ने र सजिलै व्यवस्थापन गर्न मिल्ने production वेबसाइट बनाउँछौं।\n\nतपाईंले पाउनुहुन्छ:\n• मोबाइल, ट्याब्लेट र डेस्कटपका लागि responsive layout\n• सफा HTML/CSS/JavaScript वा Flask-powered साइट\n• SEO-friendly संरचना\n• आवश्यकता अनुसार contact form, CMS र admin\n• Vercel, Linux वा तपाईंको host मा deployment",
        },
        {
            "number": "02",
            "title_en": "UI/UX Design",
            "title_ne": "UI/UX डिजाइन",
            "description_en": "Interfaces designed around users and business goals.",
            "description_ne": "प्रयोगकर्ता र व्यवसाय लक्ष्य वरिपरि डिजाइन गरिएका इन्टरफेसहरू।",
            "detail_en": "Good design is not decoration — it is how people understand and use your product.\n\nOur process:\n• Research goals, users and constraints\n• Wireframes and information architecture\n• Visual design aligned with your brand\n• Interaction patterns that feel simple\n• Handoff-ready layouts for development\n\nWe design interfaces for websites, dashboards, booking systems and internal tools.",
            "detail_ne": "राम्रो डिजाइन सजावट होइन — प्रयोगकर्ताले उत्पादन कसरी बुझ्छ र प्रयोग गर्छ भन्ने हो।\n\nप्रक्रिया:\n• लक्ष्य, प्रयोगकर्ता र सीमाहरू अनुसन्धान\n• Wireframe र information architecture\n• ब्रान्डसँग मिल्ने visual design\n• सरल interaction patterns\n• विकासका लागि तयार layout",
        },
        {
            "number": "03",
            "title_en": "Custom Software",
            "title_ne": "कस्टम सफ्टवेयर",
            "description_en": "Custom applications built around real business workflows.",
            "description_ne": "वास्तविक व्यवसाय वर्कफ्लो वरिपरि निर्माण गरिएका कस्टम एप्लिकेसनहरू।",
            "detail_en": "Off-the-shelf tools often force your team to change how they work. We build software around your actual process.\n\nTypical scope:\n• Web applications with secure login and roles\n• Forms, reports and dashboards\n• REST APIs and integrations\n• PostgreSQL / MySQL data models\n• Admin panels for day-to-day operations\n\nStack we use most: Python, Flask, HTML, CSS, JavaScript, SQL.",
            "detail_ne": "तयार सफ्टवेयरले प्रायः तपाईंको काम गर्ने तरिका बदल्न बाध्य बनाउँछ। हामी तपाईंको वास्तविक प्रक्रिया अनुसार बनाउँछौं।\n\nसामान्य दायरा:\n• सुरक्षित login र roles सहित web app\n• Form, report र dashboard\n• REST API र integration\n• PostgreSQL / MySQL data model\n• दैनिक सञ्चालनका लागि admin panel",
        },
        {
            "number": "04",
            "title_en": "Business Management Systems",
            "title_ne": "व्यवसाय व्यवस्थापन प्रणाली",
            "description_en": "HMS, CRM, HRM, ticketing, operational and internal management systems.",
            "description_ne": "HMS, CRM, HRM, टिकटिङ, सञ्चालन र आन्तरिक व्यवस्थापन प्रणालीहरू।",
            "detail_en": "End-to-end systems for running operations — not just a brochure website.\n\nExamples we have built:\n• Hotel management (rooms, orders, staff workflows)\n• Online ticketing for events and tournaments\n• Internal dashboards and record systems\n\nDeliverables usually include:\n• Role-based access for staff and managers\n• Real-time or near real-time updates\n• Reports and search\n• Mobile-friendly admin and public interfaces\n• Hosting and maintenance options",
            "detail_ne": "सञ्चालन चलाउने end-to-end प्रणाली — brochure वेबसाइट मात्र होइन।\n\nउदाहरण:\n• होटल व्यवस्थापन (कोठा, अर्डर, कर्मचारी)\n• कार्यक्रम र टुर्नामेन्टका लागि online ticketing\n• आन्तरिक dashboard र record system\n\nसामान्य deliverable:\n• Role-based access\n• Report र search\n• Mobile-friendly interface\n• Hosting र maintenance विकल्प",
        },
        {
            "number": "05",
            "title_en": "Automation",
            "title_ne": "स्वचालन",
            "description_en": "Digital workflows and integrations that reduce repetitive work.",
            "description_ne": "दोहोरिने काम घटाउने डिजिटल वर्कफ्लो र एकीकरणहरू।",
            "detail_en": "We connect tools and automate steps that your team repeats every day.\n\nExamples:\n• Form submissions to email and admin inbox\n• Status notifications to customers\n• Scheduled jobs and data sync\n• API bridges between systems\n\nGoal: less manual copy-paste, fewer errors, faster response times.",
            "detail_ne": "हामी उपकरण जोड्छौं र दैनिक दोहोरिने कदम स्वचालित बनाउँछौं।\n\nउदाहरण:\n• Form → email र admin inbox\n• ग्राहकलाई status notification\n• Scheduled job र data sync\n• प्रणालीबीच API bridge",
        },
        {
            "number": "06",
            "title_en": "Digital Solutions",
            "title_ne": "डिजिटल समाधान",
            "description_en": "Custom technology solutions for organizations and businesses.",
            "description_ne": "संगठन र व्यवसायका लागि कस्टम प्रविधि समाधानहरू।",
            "detail_en": "When the problem does not fit a single product category, we design a solution from scratch.\n\nHow we work:\n• Clarify the problem and success metrics\n• Propose architecture and timeline\n• Build, test and deploy\n• Hand over documentation and training\n• Optional ongoing support\n\nFrom school portals to sports club sites and operational tools — practical systems that ship.",
            "detail_ne": "समस्या एउटै उत्पादन श्रेणीमा नपर्दा हामी सुरुबाट समाधान डिजाइन गर्छौं।\n\nकाम गर्ने तरिका:\n• समस्या र सफलताको मापदण्ड स्पष्ट\n• Architecture र timeline प्रस्ताव\n• Build, test र deploy\n• Documentation र training\n• वैकल्पिक ongoing support",
        },
    ]
    for i, data in enumerate(services):
        existing = Service.query.filter_by(title_en=data["title_en"]).first()
        if existing:
            # fill missing detail text
            if not existing.detail_en and data.get("detail_en"):
                existing.detail_en = data["detail_en"]
            if not existing.detail_ne and data.get("detail_ne"):
                existing.detail_ne = data["detail_ne"]
            continue
        db.session.add(
            Service(
                number=data["number"],
                title_en=data["title_en"],
                title_ne=data["title_ne"],
                description_en=data["description_en"],
                description_ne=data["description_ne"],
                detail_en=data.get("detail_en"),
                detail_ne=data.get("detail_ne"),
                display_order=i,
                is_active=True,
            )
        )
    db.session.commit()


def seed_process():
    steps = [
        ("01", "Discover", "खोज", "Understand the business, problem and goals.", "व्यवसाय, समस्या र लक्ष्यहरू बुझ्नुहोस्।"),
        ("02", "Plan", "योजना", "Define structure, technology and user experience.", "संरचना, प्रविधि र प्रयोगकर्ता अनुभव परिभाषित गर्नुहोस्।"),
        ("03", "Design", "डिजाइन", "Create the visual and interaction system.", "दृश्य र अन्तरक्रिया प्रणाली सिर्जना गर्नुहोस्।"),
        ("04", "Build", "निर्माण", "Develop the actual product.", "वास्तविक उत्पादन विकास गर्नुहोस्।"),
        ("05", "Test", "परीक्षण", "Test usability, performance and responsiveness.", "उपयोगिता, प्रदर्शन र उत्तरदायित्व परीक्षण गर्नुहोस्।"),
        ("06", "Launch", "सुरुवात", "Deploy, monitor and improve.", "तैनाथ गर्नुहोस्, निगरानी गर्नुहोस् र सुधार गर्नुहोस्।"),
    ]
    for i, (num, en, ne, desc_en, desc_ne) in enumerate(steps):
        if not ProcessStep.query.filter_by(title_en=en).first():
            db.session.add(
                ProcessStep(
                    number=num,
                    title_en=en,
                    title_ne=ne,
                    description_en=desc_en,
                    description_ne=desc_ne,
                    display_order=i,
                    is_active=True,
                )
            )
    db.session.commit()


def seed_categories():
    cats = [
        ("Websites", "वेबसाइटहरू", "websites"),
        ("Systems", "प्रणालीहरू", "systems"),
        ("Sports", "खेलकुद", "sports"),
        ("Business", "व्यवसाय", "business"),
        ("UI/UX", "UI/UX", "ui-ux"),
        ("Other", "अन्य", "other"),
    ]
    for i, (en, ne, slug) in enumerate(cats):
        if not ProjectCategory.query.filter_by(slug=slug).first():
            db.session.add(
                ProjectCategory(name_en=en, name_ne=ne, slug=slug, display_order=i)
            )
    db.session.commit()


def seed_sample_projects():
    systems = ProjectCategory.query.filter_by(slug="systems").first()
    sports = ProjectCategory.query.filter_by(slug="sports").first()
    websites = ProjectCategory.query.filter_by(slug="websites").first()
    business = ProjectCategory.query.filter_by(slug="business").first()

    samples = [
        {
            "title": "Hotel Grand HMS",
            "slug": "hotel-grand-hms",
            "description_en": "Hotel management system for booking, food ordering and day-to-day operations at Hotel Grand Garden.",
            "description_ne": "Hotel Grand Garden को लागि बुकिङ, खाना अर्डर र दैनिक सञ्चालन व्यवस्थापन प्रणाली।",
            "full_description_en": "A complete hotel management platform built for Hotel Grand — covering room booking, food ordering, and operational workflows for staff and management.",
            "full_description_ne": "Hotel Grand का लागि पूर्ण होटल व्यवस्थापन प्लेटफर्म — कोठा बुकिङ, खाना अर्डर, र कर्मचारी तथा व्यवस्थापनका लागि सञ्चालन वर्कफ्लो।",
            "client": "Hotel Grand",
            "location": "Urlabari, Morang, Nepal",
            "category": systems,
            "technologies": ["Python", "Flask", "PostgreSQL", "JavaScript"],
            "cover_image": "/static/images/projects/hotel-grand.jpg",
            "live_url": "https://hms.hotelgrand.com.np/",
            "project_year": "2025",
            "status": "Live",
            "challenge_en": "Hotel operations needed a single system for rooms, orders and staff workflows instead of scattered tools.",
            "challenge_ne": "होटल सञ्चालनमा कोठा, अर्डर र कर्मचारी वर्कफ्लोका लागि छरिएका उपकरणहरूको सट्टा एउटै प्रणाली चाहिन्थ्यो।",
            "solution_en": "Built Hotel Grand Garden HMS — booking, food ordering and operational modules tailored to daily hotel work.",
            "solution_ne": "Hotel Grand Garden HMS निर्माण — दैनिक होटल कामअनुसार बुकिङ, खाना अर्डर र सञ्चालन मोड्युलहरू।",
            "features_en": "Room booking\nFood ordering\nStaff operational flows\nSecure login",
            "features_ne": "कोठा बुकिङ\nखाना अर्डर\nकर्मचारी सञ्चालन प्रवाह\nसुरक्षित लगइन",
            "result_en": "Live system used for hotel operations at Hotel Grand.",
            "result_ne": "Hotel Grand मा होटल सञ्चालनका लागि लाइभ प्रणाली।",
            "is_featured": True,
            "is_published": True,
            "display_order": 1,
        },
        {
            "title": "Hotel Grand",
            "slug": "hotel-grand",
            "description_en": "Official website for Hotel Grand — family restaurant and lodge in Urlabari, Morang.",
            "description_ne": "Urlabari, Morang स्थित Hotel Grand — परिवारिक रेस्टुरेन्ट र लजको आधिकारिक वेबसाइट।",
            "full_description_en": "Marketing and information website for Hotel Grand Family Restaurant & Lodge, showcasing rooms, dining, and location in Urlabari, Morang.",
            "client": "Hotel Grand",
            "location": "Urlabari, Morang, Nepal",
            "category": websites,
            "technologies": ["HTML", "CSS", "JavaScript"],
            "cover_image": "/static/images/projects/hotel-grand.jpg",
            "live_url": "https://hotelgrand.com.np/",
            "project_year": "2025",
            "status": "Live",
            "challenge_en": "Hotel Grand needed a clear public website for restaurant and lodge visitors in Urlabari.",
            "solution_en": "Designed and developed a responsive marketing site with rooms, dining and location information.",
            "features_en": "Responsive layout\nService overview\nContact and location",
            "result_en": "Public website live at hotelgrand.com.np.",
            "is_featured": True,
            "is_published": True,
            "display_order": 2,
        },
        {
            "title": "Leaf Letang Enterprises",
            "slug": "leaf-letang-enterprises",
            "description_en": "Website for Leaf Letang Enterprises — sustainable leaf products from Nepal.",
            "description_ne": "Leaf Letang Enterprises को वेबसाइट — नेपालबाट दिगो पातजन्य उत्पादनहरू।",
            "full_description_en": "Digital presence for Leaf Letang Enterprises, highlighting sustainable leaf-based products sourced from Nepal.",
            "client": "Leaf Letang Enterprises",
            "location": "Nepal",
            "category": business if business else websites,
            "technologies": ["HTML", "CSS", "JavaScript", "Vercel"],
            "cover_image": "/static/images/projects/leaf-letang.jpg",
            "live_url": "https://leafltg.vercel.app/",
            "project_year": "2025",
            "status": "Live",
            "challenge_en": "Leaf Letang Enterprises needed a digital presence for sustainable leaf products from Nepal.",
            "solution_en": "Built a clean product-focused website deployed on Vercel.",
            "features_en": "Product storytelling\nResponsive design\nFast deployment",
            "result_en": "Live site at leafltg.vercel.app.",
            "is_featured": True,
            "is_published": True,
            "display_order": 3,
        },
        {
            "title": "New Vision Academy",
            "slug": "new-vision-academy",
            "description_en": "School website for New Vision Academy, Urlabari-8, Morang — ECD to Grade 10.",
            "description_ne": "New Vision Academy (Urlabari-8, Morang) को विद्यालय वेबसाइट — ECD देखि कक्षा १० सम्म।",
            "full_description_en": "Institutional website for New Vision Academy presenting programs from early childhood to Grade 10 in Urlabari, Morang.",
            "client": "New Vision Academy",
            "location": "Urlabari-8, Morang, Nepal",
            "category": websites,
            "technologies": ["HTML", "CSS", "JavaScript"],
            "cover_image": "/static/images/projects/academy.jpg",
            "live_url": "https://www.newvisionacademy.com.np/",
            "project_year": "2025",
            "status": "Live",
            "challenge_en": "The academy needed an institutional website covering ECD to Grade 10 programs.",
            "solution_en": "Delivered a school website with program information for parents and visitors.",
            "features_en": "Program overview\nInstitutional branding\nContact channels",
            "result_en": "Live at newvisionacademy.com.np.",
            "is_featured": True,
            "is_published": True,
            "display_order": 4,
        },
        {
            "title": "Pathari Sanischare Gold Cup",
            "slug": "pathari-sanischare-gold-cup",
            "description_en": "Online ticketing system for Pathari Sanischare Gold Cup football tournament.",
            "description_ne": "Pathari Sanischare Gold Cup फुटबल टूर्नामेन्टको अनलाइन टिकटिङ प्रणाली।",
            "full_description_en": "Official online ticket booking platform for the Pathari Sanischare Gold Cup — enabling fans to buy tournament tickets digitally.",
            "client": "Pathari Sanischare Gold Cup",
            "location": "Pathari, Nepal",
            "category": sports,
            "technologies": ["Python", "Flask", "PostgreSQL"],
            "cover_image": "/static/images/projects/gold-cup.jpg",
            "live_url": "https://ticketpathrigc.argan.com.np/",
            "project_year": "2026",
            "status": "Live",
            "challenge_en": "Tournament organizers needed official online ticket sales for Pathari Sanischare Gold Cup.",
            "solution_en": "Built a ticketing platform so fans can buy official football tickets online.",
            "features_en": "Online ticket purchase\nEvent-focused flows\nAdmin-ready structure",
            "result_en": "Live ticketing at ticketpathrigc.argan.com.np.",
            "is_featured": True,
            "is_published": True,
            "display_order": 5,
        },
        {
            "title": "Pathari-11 FC",
            "slug": "pathari-11-fc",
            "description_en": "Official website of Pathari-11 FC football club.",
            "description_ne": "Pathari-11 FC फुटबल क्लबको आधिकारिक वेबसाइट।",
            "full_description_en": "Club website for Pathari-11 FC with team presence and football club information.",
            "client": "Pathari-11 FC",
            "location": "Pathari, Nepal",
            "category": sports,
            "technologies": ["HTML", "CSS", "JavaScript"],
            "cover_image": "/static/images/projects/gold-cup.jpg",
            "live_url": "https://pathri11fc.argan.com.np/",
            "project_year": "2025",
            "status": "Live",
            "challenge_en": "Pathari-11 FC needed an official club web presence.",
            "solution_en": "Developed the club website for team and community visibility.",
            "features_en": "Club identity\nResponsive pages",
            "result_en": "Live at pathri11fc.argan.com.np.",
            "is_featured": True,
            "is_published": True,
            "display_order": 6,
        },
        {
            "title": "Jhapa FC",
            "slug": "jhapa-fc",
            "description_en": "Official website of Jhapa FC football club.",
            "description_ne": "Jhapa FC फुटबल क्लबको आधिकारिक वेबसाइट।",
            "full_description_en": "Digital platform for Jhapa FC — official football club website.",
            "client": "Jhapa FC",
            "location": "Jhapa, Nepal",
            "category": sports,
            "technologies": ["HTML", "CSS", "JavaScript", "Vercel"],
            "cover_image": "/static/images/projects/jhapa-fc.jpg",
            "live_url": "https://jhapacityfc.vercel.app/",
            "project_year": "2025",
            "status": "Live",
            "challenge_en": "Jhapa FC required an official football club website.",
            "solution_en": "Built and deployed the club site on Vercel.",
            "features_en": "Club branding\nFast hosting",
            "result_en": "Live at jhapacityfc.vercel.app.",
            "is_featured": True,
            "is_published": True,
            "display_order": 7,
        },
    ]
    for s in samples:
        if not Project.query.filter_by(slug=s["slug"]).first():
            cat = s.pop("category")
            # handle "business or websites"
            if cat is None:
                cat = websites
            p = Project(**s, category_id=cat.id if cat else None)
            db.session.add(p)
    db.session.commit()



def seed_tech():
    techs = [
        "Python", "Flask", "HTML5", "CSS3", "JavaScript",
        "PostgreSQL", "MySQL", "SQL", "REST API", "Git", "Linux", "Vercel",
    ]
    for i, name in enumerate(techs):
        if not TechItem.query.filter_by(name=name).first():
            db.session.add(TechItem(name=name, display_order=i, is_active=True))
    db.session.commit()


def seed_stats():
    # Only substantiated numbers from real delivered work
    stats = [
        ("7+", "Projects Delivered", "डेलिभर परियोजनाहरू", 0),
        ("5+", "Websites", "वेबसाइटहरू", 1),
        ("2+", "Business Systems", "व्यवसाय प्रणालीहरू", 2),
        ("12+", "Technologies", "प्रविधिहरू", 3),
        ("Nepal", "Based", "आधारित", 4),
    ]
    for value, en, ne, order in stats:
        if not StatItem.query.filter_by(label_en=en).first():
            db.session.add(StatItem(value=value, label_en=en, label_ne=ne, display_order=order, is_active=True))
    db.session.commit()


def seed_faqs():
    faqs = [
        (
            "How much does a website cost?",
            "वेबसाइटको लागत कति हुन्छ?",
            "Cost depends on scope — pages, features, integrations and whether you need a custom system. Share your requirements and we will propose a clear package.",
            "लागत स्कोपमा निर्भर गर्छ — पृष्ठहरू, सुविधाहरू, एकीकरण र कस्टम प्रणाली आवश्यक छ कि छैन। आवश्यकता बताउनुहोस्, हामी स्पष्ट प्याकेज प्रस्ताव गर्छौं।",
        ),
        (
            "How long does development take?",
            "विकासमा कति समय लाग्छ?",
            "A standard marketing website often takes 1–3 weeks. Custom business systems typically take several weeks depending on complexity.",
            "सामान्य मार्केटिङ वेबसाइट प्रायः १–३ हप्तामा बन्छ। कस्टम व्यवसाय प्रणाली जटिलता अनुसार केही हप्ता लाग्न सक्छ।",
        ),
        (
            "Do you provide hosting?",
            "के तपाईं होस्टिङ प्रदान गर्नुहुन्छ?",
            "Yes. We can deploy on Vercel, Cloudflare-compatible setups, or your preferred host and guide DNS configuration.",
            "हो। हामी Vercel, Cloudflare-compatible सेटअप वा तपाईंको मनपर्ने होस्टमा डिप्लोय गर्न सक्छौं र DNS सेटअपमा सहयोग गर्छौं।",
        ),
        (
            "Do you provide maintenance?",
            "के तपाईं मर्मतसम्भार प्रदान गर्नुहुन्छ?",
            "Yes. Ongoing updates, security checks and small feature improvements can be arranged after launch.",
            "हो। लन्च पछि अपडेट, सुरक्षा जाँच र साना सुविधा सुधारहरू व्यवस्था गर्न सकिन्छ।",
        ),
        (
            "Can you build custom business software?",
            "के तपाईं कस्टम व्यवसाय सफ्टवेयर बनाउन सक्नुहुन्छ?",
            "Yes. We build practical systems such as hotel management, ticketing, internal tools and workflow automation.",
            "हो। हामी होटल व्यवस्थापन, टिकटिङ, आन्तरिक उपकरण र वर्कफ्लो स्वचालन जस्ता व्यावहारिक प्रणाली बनाउँछौं।",
        ),
        (
            "Do you work with clients outside Nepal?",
            "के तपाईं नेपाल बाहिरका ग्राहकसँग काम गर्नुहुन्छ?",
            "Yes. Communication is primarily online and projects can be delivered remotely.",
            "हो। सञ्चार मुख्यतया अनलाइन हुन्छ र परियोजनाहरू रिमोटबाट डेलिभर गर्न सकिन्छ।",
        ),
    ]
    for i, (qe, qn, ae, an) in enumerate(faqs):
        if not FAQ.query.filter_by(question_en=qe).first():
            db.session.add(FAQ(question_en=qe, question_ne=qn, answer_en=ae, answer_ne=an, display_order=i, is_active=True))
    db.session.commit()


def seed_team():
    if not TeamMember.query.filter_by(name="Argon Bhujel").first():
        db.session.add(TeamMember(
            name="Argon Bhujel",
            position_en="Founder & Full-Stack Developer",
            position_ne="संस्थापक र फुल-स्ट्याक डेभलपर",
            bio_en="Founder of BAM Studio. Designs and builds websites, business systems and digital products from the ground up.",
            bio_ne="BAM Studio का संस्थापक। वेबसाइट, व्यवसाय प्रणाली र डिजिटल उत्पादनहरू सुरुदेखि डिजाइन र निर्माण गर्छन्।",
            skills=["Python", "Flask", "JavaScript", "PostgreSQL", "UI/UX"],
            social_links={"github": "https://github.com", "linkedin": "https://linkedin.com"},
            display_order=0,
            is_active=True,
        ))
        db.session.commit()


def seed_founder_settings():
    founder = [
        ("founder_name", "Argon Bhujel", "Argon Bhujel", "founder"),
        ("founder_title", "Founder & Full-Stack Developer", "संस्थापक र फुल-स्ट्याक डेभलपर", "founder"),
        ("founder_bio", "I don't just design websites. I build the systems behind them. At BAM Studio I work with businesses to ship practical digital products — from marketing sites to hotel management and ticketing platforms.", "म वेबसाइट मात्र डिजाइन गर्दिनँ। म तिनका पछाडिका प्रणालीहरू निर्माण गर्छु। BAM Studio मा म व्यवसायसँग मिलेर व्यावहारिक डिजिटल उत्पादन डेलिभर गर्छु।", "founder"),
        ("founder_philosophy", "Build from scratch. Keep it maintainable. Ship real products that operators can use every day.", "सुरुदेखि बनाउनुहोस्। मर्मतयोग्य राख्नुहोस्। सञ्चालकहरूले दैनिक प्रयोग गर्न सक्ने वास्तविक उत्पादन डेलिभर गर्नुहोस्।", "founder"),
        ("founder_github", "https://github.com", None, "founder"),
        ("founder_linkedin", "https://linkedin.com", None, "founder"),
        ("founder_website", "https://argan.com.np", None, "founder"),
        ("hero_bg_image", "", None, "homepage"),
    ]
    for key, en, ne, group in founder:
        if not SiteSetting.query.filter_by(key=key).first():
            db.session.add(SiteSetting(key=key, value_en=en, value_ne=ne, group=group))
    db.session.commit()



def seed_admin():
    """Create default Super Admin if none exists."""
    if AdminUser.query.first():
        return
    role = Role.query.filter_by(name="Super Admin").first()
    if not role:
        role = Role(name="Super Admin", description="Full system access")
        db.session.add(role)
        db.session.flush()
    user = AdminUser(
        email="argon.bhujel@bamstudio.com",
        username="argon.bhujel",
        full_name="Argon Bhujel",
        role_id=role.id,
        is_active=True,
    )
    user.set_password("Bam@2026#")
    db.session.add(user)
    db.session.commit()
    print("Default admin created: argon.bhujel / Bam@2026#")



def seed_clients():
    from app.models import Client
    names = [
        ("Hotel Grand", "https://hotelgrand.com.np/", 0),
        ("Leaf Letang Enterprises", "https://leafltg.vercel.app/", 1),
        ("New Vision Academy", "https://www.newvisionacademy.com.np/", 2),
        ("Pathari Sanischare Gold Cup", "https://ticketpathrigc.argan.com.np/", 3),
        ("Pathari-11 FC", "https://pathri11fc.argan.com.np/", 4),
        ("Jhapa FC", "https://jhapacityfc.vercel.app/", 5),
    ]
    for name, url, order in names:
        if not Client.query.filter_by(name=name).first():
            db.session.add(Client(name=name, website_url=url, display_order=order, is_active=True))
    db.session.commit()

def run_seed():
    """Idempotent seed. Safe under concurrent cold starts (IntegrityError → skip)."""
    from sqlalchemy.exc import IntegrityError
    from app import db

    steps = [
        seed_roles,
        seed_settings,
        seed_navigation,
        seed_services,
        seed_process,
        seed_categories,
        seed_sample_projects,
        seed_tech,
        seed_stats,
        seed_faqs,
        seed_team,
        seed_founder_settings,
        seed_clients,
        seed_admin,
    ]
    for step in steps:
        try:
            step()
        except IntegrityError:
            db.session.rollback()
        except Exception:
            db.session.rollback()
            raise
    print("Seed completed.")
