"""
Comprehensive Cities Data Mapping for Major Countries and States
"""

# Major cities data for comprehensive country/state coverage
CITIES_DATA = {
    "US": {  # United States
        "California": [
            "Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno", "Sacramento",
            "Long Beach", "Oakland", "Bakersfield", "Anaheim", "Santa Ana", "Riverside",
            "Stockton", "Irvine", "Chula Vista", "Fremont", "San Bernardino", "Modesto",
            "Fontana", "Oxnard", "Moreno Valley", "Huntington Beach", "Glendale", "Santa Clarita"
        ],
        "New York": [
            "New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany",
            "New Rochelle", "Mount Vernon", "Schenectady", "Utica", "White Plains", "Hempstead",
            "Troy", "Niagara Falls", "Binghamton", "Freeport", "Valley Stream", "Long Beach",
            "Rome", "Watertown", "Ithaca", "Middletown", "Spring Valley", "Glen Cove"
        ],
        "Texas": [
            "Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso", "Arlington",
            "Corpus Christi", "Plano", "Laredo", "Lubbock", "Garland", "Irving", "Amarillo",
            "Grand Prairie", "Brownsville", "McKinney", "Frisco", "Pasadena", "Mesquite",
            "Killeen", "McAllen", "Waco", "Carrollton", "Pearland", "Denton"
        ],
        "Florida": [
            "Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg", "Hialeah",
            "Tallahassee", "Fort Lauderdale", "Port St. Lucie", "Cape Coral", "Pembroke Pines",
            "Hollywood", "Miramar", "Gainesville", "Coral Springs", "Miami Gardens", "Clearwater",
            "Palm Bay", "West Palm Beach", "Pompano Beach", "Lakeland", "Davie"
        ],
        "Illinois": [
            "Chicago", "Aurora", "Rockford", "Joliet", "Naperville", "Springfield", "Peoria",
            "Elgin", "Waukegan", "Cicero", "Champaign", "Bloomington", "Arlington Heights",
            "Evanston", "Decatur", "Schaumburg", "Bolingbrook", "Palatine", "Skokie", "Des Plaines"
        ]
    },
    
    "CA": {  # Canada
        "Ontario": [
            "Toronto", "Ottawa", "Mississauga", "Brampton", "Hamilton", "London", "Markham",
            "Vaughan", "Kitchener", "Windsor", "Richmond Hill", "Oakville", "Burlington",
            "Sudbury", "Oshawa", "Barrie", "St. Catharines", "Cambridge", "Kingston", "Whitby",
            "Guelph", "Thunder Bay", "Waterloo", "Brantford", "Pickering", "Niagara Falls"
        ],
        "Quebec": [
            "Montreal", "Quebec City", "Laval", "Gatineau", "Longueuil", "Sherbrooke", "Saguenay",
            "Lévis", "Trois-Rivières", "Terrebonne", "Saint-Jean-sur-Richelieu", "Repentigny",
            "Brossard", "Drummondville", "Saint-Jérôme", "Granby", "Blainville", "Saint-Hyacinthe",
            "Shawinigan", "Dollard-des-Ormeaux", "Joliette", "Rimouski", "Mirabel", "Boucherville"
        ],
        "British Columbia": [
            "Vancouver", "Surrey", "Burnaby", "Richmond", "Abbotsford", "Coquitlam", "Victoria",
            "Saanich", "Delta", "Kelowna", "Langley", "Kamloops", "Nanaimo", "Prince George",
            "Chilliwack", "New Westminster", "White Rock", "North Vancouver", "Vernon", "Penticton",
            "Campbell River", "Courtenay", "Cranbrook", "Fort St. John", "Powell River"
        ],
        "Alberta": [
            "Calgary", "Edmonton", "Red Deer", "Lethbridge", "St. Albert", "Medicine Hat",
            "Grande Prairie", "Airdrie", "Spruce Grove", "Okotoks", "Lloydminster", "Fort McMurray",
            "Leduc", "Camrose", "Brooks", "Cold Lake", "Wetaskiwin", "Stony Plain", "Lacombe"
        ]
    },
    
    "IN": {  # India
        "Maharashtra": [
            "Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Kolhapur", "Sangli",
            "Ahmednagar", "Latur", "Jalgaon", "Akola", "Satara", "Chandrapur", "Parbhani",
            "Ichalkaranji", "Jalna", "Ambajogai", "Nanded", "Yavatmal", "Wardha", "Amravati",
            "Beed", "Osmanabad", "Washim", "Hingoli", "Gadchiroli", "Gondia", "Bhandara"
        ],
        "Karnataka": [
            "Bangalore", "Mysore", "Hubli", "Dharwad", "Mangalore", "Belgaum", "Gulbarga",
            "Davanagere", "Ballari", "Bijapur", "Shimoga", "Tumkur", "Raichur", "Bidar",
            "Hospet", "Gadag", "Udupi", "Chikmagalur", "Hassan", "Mandya", "Chitradurga",
            "Kolar", "Bagalkot", "Davangere", "Haveri", "Koppal", "Bellary", "Ramanagara"
        ],
        "Tamil Nadu": [
            "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli",
            "Tiruppur", "Vellore", "Thoothukudi", "Nagercoil", "Thanjavur", "Dindigul",
            "Cuddalore", "Kanchipuram", "Erode", "Tiruvannamalai", "Pollachi", "Rajapalayam",
            "Sivakasi", "Pudukkottai", "Neyveli", "Nagapattinam", "Viluppuram", "Tiruvallur"
        ],
        "Delhi": [
            "New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi", "Central Delhi",
            "North East Delhi", "North West Delhi", "South East Delhi", "South West Delhi",
            "Shahdara", "Ghaziabad", "Noida", "Faridabad", "Gurgaon", "Greater Noida", "Sonipat",
            "Rohtak", "Panipat", "Bahadurgarh", "Meerut", "Hapur", "Bulandshahr", "Muzaffarnagar"
        ],
        "Gujarat": [
            "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Junagadh",
            "Gandhinagar", "Anand", "Navsari", "Morbi", "Mehsana", "Surendranagar", "Bharuch",
            "Vapi", "Veraval", "Porbandar", "Godhra", "Botad", "Amreli", "Palanpur", "Deesa",
            "Jetpur", "Kalol", "Dahod", "Bhuj", "Nadiad", "Valsad", "Upleta", "Una"
        ],
        "Uttar Pradesh": [
            "Lucknow", "Kanpur", "Ghaziabad", "Agra", "Varanasi", "Meerut", "Allahabad", "Bareilly",
            "Aligarh", "Moradabad", "Saharanpur", "Gorakhpur", "Noida", "Firozabad", "Loni",
            "Muzaffarnagar", "Mathura", "Rampur", "Shahjahanpur", "Farrukhabad", "Mau", "Hapur",
            "Etawah", "Mirzapur", "Bulandshahr", "Sambhal", "Amroha", "Hardoi", "Fatehpur", "Raebareli"
        ],
        "West Bengal": [
            "Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Malda", "Bardhaman", "Baharampur",
            "Habra", "Kharagpur", "Shantipur", "Dankuni", "Dhulian", "Ranaghat", "Haldia", "Raiganj",
            "Krishnanagar", "Nabadwip", "Medinipur", "Jalpaiguri", "Balurghat", "Basirhat", "Bankura",
            "Purulia", "Tamluk", "Midnapore", "Cooch Behar", "Alipurduar", "Darjeeling", "Kalimpong"
        ],
        "Rajasthan": [
            "Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar", "Bharatpur",
            "Pali", "Bhilwara", "Sri Ganganagar", "Kishangarh", "Baran", "Dhaulpur", "Tonk",
            "Beawar", "Hanumangarh", "Sikar", "Jhunjhunu", "Barmer", "Jaisalmer", "Banswara",
            "Bundi", "Sawai Madhopur", "Jhalawar", "Nagaur", "Churu", "Dungarpur", "Mount Abu"
        ],
        "Punjab": [
            "Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Firozpur",
            "Batala", "Pathankot", "Moga", "Abohar", "Malerkotla", "Khanna", "Phagwara",
            "Muktsar", "Barnala", "Rajpura", "Hoshiarpur", "Kapurthala", "Faridkot", "Sunam",
            "Sangrur", "Nawanshahr", "Gurdaspur", "Kharar", "Gobindgarh", "Mansa", "Malout"
        ],
        "Haryana": [
            "Faridabad", "Gurgaon", "Panipat", "Ambala", "Yamunanagar", "Rohtak", "Hisar",
            "Karnal", "Sonipat", "Panchkula", "Bhiwani", "Sirsa", "Bahadurgarh", "Jind",
            "Thanesar", "Kaithal", "Rewari", "Narnaul", "Pundri", "Kosli", "Palwal", "Hansi",
            "Mahendragarh", "Ladwa", "Sohna", "Mewat", "Fatehabad", "Dabwali", "Tohana", "Jhajjar"
        ]
    },
    
    "GB": {  # United Kingdom
        "England": [
            "London", "Birmingham", "Manchester", "Liverpool", "Leeds", "Sheffield", "Bristol",
            "Newcastle", "Nottingham", "Leicester", "Coventry", "Bradford", "Stoke-on-Trent",
            "Wolverhampton", "Plymouth", "Derby", "Southampton", "Portsmouth", "Brighton",
            "Reading", "Northampton", "Luton", "Warrington", "Bournemouth", "Peterborough",
            "Cambridge", "Oxford", "York", "Exeter", "Gloucester", "Bath", "Chester", "Canterbury"
        ],
        "Scotland": [
            "Glasgow", "Edinburgh", "Aberdeen", "Dundee", "Stirling", "Perth", "Inverness",
            "Paisley", "East Kilbride", "Livingston", "Hamilton", "Cumbernauld", "Kirkcaldy",
            "Dunfermline", "Ayr", "Kilmarnock", "Greenock", "Coatbridge", "Glenrothes", "Airdrie",
            "Falkirk", "Motherwell", "Irvine", "Dumfries", "Rutherglen", "Wishaw", "Clydebank"
        ],
        "Wales": [
            "Cardiff", "Swansea", "Newport", "Wrexham", "Barry", "Caerphilly", "Bridgend",
            "Neath", "Port Talbot", "Cwmbran", "Rhondda", "Merthyr Tydfil", "Llanelli",
            "Colwyn Bay", "Flint", "Ebbw Vale", "Pontypool", "Maesteg", "Carmarthen", "Bangor",
            "Aberdare", "Abergavenny", "Holyhead", "Brecon", "Tenby", "Haverfordwest", "Conwy"
        ],
        "Northern Ireland": [
            "Belfast", "Derry", "Lisburn", "Newtownabbey", "Bangor", "Craigavon", "Castlereagh",
            "Ballymena", "Newry", "Carrickfergus", "Coleraine", "Omagh", "Larne", "Strabane",
            "Limavady", "Enniskillen", "Armagh", "Cookstown", "Downpatrick", "Dungannon",
            "Antrim", "Ballymoney", "Magherafelt", "Newcastle", "Portstewart", "Ballycastle"
        ]
    },
    
    "DE": {  # Germany
        "Bavaria": [
            "Munich", "Nuremberg", "Augsburg", "Würzburg", "Regensburg", "Ingolstadt", "Fürth",
            "Erlangen", "Bayreuth", "Bamberg", "Aschaffenburg", "Landshut", "Passau", "Freising",
            "Rosenheim", "Neu-Ulm", "Schweinfurt", "Coburg", "Hof", "Kempten", "Ansbach",
            "Dachau", "Amberg", "Weiden", "Forchheim", "Lindau", "Günzburg", "Deggendorf"
        ],
        "North Rhine-Westphalia": [
            "Cologne", "Düsseldorf", "Dortmund", "Essen", "Duisburg", "Bochum", "Wuppertal",
            "Bielefeld", "Bonn", "Münster", "Mönchengladbach", "Gelsenkirchen", "Aachen",
            "Krefeld", "Oberhausen", "Hagen", "Hamm", "Mülheim an der Ruhr", "Leverkusen",
            "Solingen", "Osnabrück", "Herne", "Neuss", "Paderborn", "Recklinghausen", "Bottrop"
        ],
        "Baden-Württemberg": [
            "Stuttgart", "Mannheim", "Karlsruhe", "Freiburg", "Heidelberg", "Ulm", "Heilbronn",
            "Pforzheim", "Reutlingen", "Esslingen", "Ludwigsburg", "Tübingen", "Villingen-Schwenningen",
            "Konstanz", "Sindelfingen", "Aalen", "Böblingen", "Ravensburg", "Friedrichshafen",
            "Göppingen", "Offenburg", "Schwäbisch Gmünd", "Waiblingen", "Fellbach", "Weinheim"
        ],
        "Hesse": [
            "Frankfurt", "Wiesbaden", "Kassel", "Darmstadt", "Offenbach", "Hanau", "Marburg",
            "Gießen", "Fulda", "Rüsselsheim", "Wetzlar", "Bad Hersfeld", "Oberursel", "Rodgau",
            "Dreieich", "Bensheim", "Maintal", "Lampertheim", "Limburg", "Viernheim", "Neu-Isenburg"
        ],
        "Lower Saxony": [
            "Hanover", "Braunschweig", "Oldenburg", "Osnabrück", "Wolfsburg", "Göttingen",
            "Salzgitter", "Hildesheim", "Delmenhorst", "Wilhelmshaven", "Lüneburg", "Celle",
            "Garbsen", "Hameln", "Lingen", "Langenhagen", "Nordhorn", "Wolfenbüttel", "Goslar",
            "Peine", "Emden", "Cuxhaven", "Stade", "Melle", "Neustadt", "Leer", "Buchholz"
        ]
    },
    
    "FR": {  # France
        "Île-de-France": [
            "Paris", "Boulogne-Billancourt", "Saint-Denis", "Argenteuil", "Montreuil", "Créteil",
            "Nanterre", "Colombes", "Versailles", "Aulnay-sous-Bois", "Rueil-Malmaison", "Aubervilliers",
            "Champigny-sur-Marne", "Saint-Maur-des-Fossés", "Drancy", "Issy-les-Moulineaux",
            "Levallois-Perret", "Noisy-le-Grand", "Antony", "Neuilly-sur-Seine", "Clichy", "Sarcelles"
        ],
        "Provence-Alpes-Côte d'Azur": [
            "Marseille", "Nice", "Toulon", "Aix-en-Provence", "Antibes", "Cannes", "Avignon",
            "La Seyne-sur-Mer", "Hyères", "Fréjus", "Arles", "Cagnes-sur-Mer", "Grasse",
            "Draguignan", "Gap", "Salon-de-Provence", "Istres", "Martigues", "Aubagne", "Carpentras"
        ],
        "Auvergne-Rhône-Alpes": [
            "Lyon", "Grenoble", "Saint-Étienne", "Villeurbanne", "Clermont-Ferrand", "Chambéry",
            "Valence", "Annecy", "Bourg-en-Bresse", "Roanne", "Saint-Priest", "Vénissieux",
            "Montluçon", "Annemasse", "Caluire-et-Cuire", "Thonon-les-Bains", "Romans-sur-Isère",
            "Voiron", "Bourgoin-Jallieu", "Vienne", "Privas", "Le Puy-en-Velay", "Aurillac"
        ]
    },
    
    "BR": {  # Brazil
        "São Paulo": [
            "São Paulo", "Guarulhos", "Campinas", "São Bernardo do Campo", "Santo André", "Osasco",
            "Ribeirão Preto", "Sorocaba", "Santos", "Mauá", "São José dos Campos", "Mogi das Cruzes",
            "Diadema", "Jundiaí", "Piracicaba", "Carapicuíba", "Bauru", "Franca", "São Vicente",
            "Itaquaquecetuba", "Guarujá", "Taubaté", "Praia Grande", "Limeira", "Suzano", "Taboão da Serra"
        ],
        "Rio de Janeiro": [
            "Rio de Janeiro", "São Gonçalo", "Duque de Caxias", "Nova Iguaçu", "Niterói",
            "Campos dos Goytacazes", "Belford Roxo", "São João de Meriti", "Petrópolis", "Volta Redonda",
            "Magé", "Itaboraí", "Mesquita", "Nova Friburgo", "Barra Mansa", "Macaé", "Cabo Frio",
            "Angra dos Reis", "Teresópolis", "Queimados", "Nilópolis", "Resende", "Araruama"
        ],
        "Minas Gerais": [
            "Belo Horizonte", "Uberlândia", "Contagem", "Juiz de Fora", "Betim", "Montes Claros",
            "Ribeirão das Neves", "Uberaba", "Governador Valadares", "Ipatinga", "Sete Lagoas",
            "Divinópolis", "Santa Luzia", "Ibirité", "Poços de Caldas", "Patos de Minas", "Pouso Alegre",
            "Teófilo Otoni", "Barbacena", "Sabará", "Vespasiano", "Araguari", "Conselheiro Lafaiete"
        ]
    },
    
    "IT": {  # Italy
        "Lombardy": [
            "Milan", "Brescia", "Bergamo", "Monza", "Varese", "Cremona", "Mantua", "Pavia",
            "Como", "Lecco", "Lodi", "Sondrio", "Busto Arsizio", "Cinisello Balsamo", "Sesto San Giovanni",
            "Rho", "Bollate", "Desio", "Vigevano", "Seregno", "Gallarate", "Limbiate", "Corsico"
        ],
        "Lazio": [
            "Rome", "Latina", "Aprilia", "Viterbo", "Guidonia Montecelio", "Fiumicino", "Tivoli",
            "Anzio", "Pomezia", "Terracina", "Velletri", "Civitavecchia", "Frosinone", "Rieti",
            "Cassino", "Formia", "Albano Laziale", "Marino", "Ardea", "Nettuno", "Frascati"
        ],
        "Campania": [
            "Naples", "Salerno", "Giugliano in Campania", "Torre del Greco", "Pozzuoli", "Casoria",
            "Marano di Napoli", "Afragola", "Caserta", "Castellammare di Stabia", "Portici", "Acerra",
            "Ercolano", "Aversa", "Cava de' Tirreni", "Benevento", "Battipaglia", "Nocera Inferiore"
        ]
    },
    
    "ES": {  # Spain
        "Madrid": [
            "Madrid", "Móstoles", "Alcalá de Henares", "Fuenlabrada", "Leganés", "Getafe",
            "Alcorcón", "Torrejón de Ardoz", "Parla", "Alcobendas", "Las Rozas de Madrid",
            "San Sebastián de los Reyes", "Pozuelo de Alarcón", "Coslada", "Valdemoro", "Rivas-Vaciamadrid",
            "Majadahonda", "Collado Villalba", "Aranjuez", "Arganda del Rey", "Boadilla del Monte"
        ],
        "Catalonia": [
            "Barcelona", "L'Hospitalet de Llobregat", "Badalona", "Terrassa", "Sabadell", "Lleida",
            "Tarragona", "Mataró", "Santa Coloma de Gramenet", "Reus", "Girona", "Cornellà de Llobregat",
            "Sant Boi de Llobregat", "Manresa", "Rubí", "Vilanova i la Geltrú", "Castelldefels",
            "Viladecans", "El Prat de Llobregat", "Granollers", "Cerdanyola del Vallès", "Mollet del Vallès"
        ],
        "Valencia": [
            "Valencia", "Alicante", "Elche", "Castellón de la Plana", "Torrevieja", "Orihuela",
            "Gandia", "Sagunto", "Alzira", "San Vicente del Raspeig", "Elda", "Benidorm", "Alcoy",
            "Cullera", "Denia", "Villena", "Xàtiva", "Petrer", "Crevillent", "Torrent", "Paterna"
        ]
    },
    
    "JP": {  # Japan
        "Tokyo": [
            "Shibuya", "Shinjuku", "Minato", "Chiyoda", "Chuo", "Taito", "Sumida", "Koto",
            "Shinagawa", "Meguro", "Ota", "Setagaya", "Shibuya", "Nakano", "Suginami", "Toshima",
            "Kita", "Arakawa", "Itabashi", "Nerima", "Adachi", "Katsushika", "Edogawa", "Hachioji"
        ],
        "Osaka": [
            "Osaka", "Sakai", "Higashiosaka", "Hirakata", "Toyonaka", "Suita", "Takatsuki", "Neyagawa",
            "Yao", "Ibaraki", "Kadoma", "Matsubara", "Daito", "Kashiwara", "Ikeda", "Izumisano",
            "Tondabayashi", "Kawachinagano", "Izumi", "Osakasayama", "Katano", "Takaishi", "Fujiidera"
        ],
        "Kanagawa": [
            "Yokohama", "Kawasaki", "Sagamihara", "Fujisawa", "Chigasaki", "Hiratsuka", "Machida",
            "Odawara", "Yamato", "Fujisawa", "Atsugi", "Zama", "Miura", "Hadano", "Ito", "Ebina",
            "Zushi", "Ayase", "Isehara", "座間", "Minamiashigara", "Hayama", "Ninomiya", "Yugawara"
        ]
    },
    
    "CN": {  # China
        "Guangdong": [
            "Guangzhou", "Shenzhen", "Dongguan", "Foshan", "Zhuhai", "Zhongshan", "Jiangmen",
            "Huizhou", "Zhaoqing", "Maoming", "Shaoguan", "Zhanjiang", "Yangjiang", "Meizhou",
            "Qingyuan", "Chaozhou", "Jieyang", "Yunfu", "Heyuan", "Shantou", "Shanwei", "Leizhou"
        ],
        "Beijing": [
            "Dongcheng", "Xicheng", "Chaoyang", "Fengtai", "Shijingshan", "Haidian", "Mentougou",
            "Fangshan", "Tongzhou", "Shunyi", "Changping", "Daxing", "Huairou", "Pinggu",
            "Miyun", "Yanqing"
        ],
        "Shanghai": [
            "Huangpu", "Xuhui", "Changning", "Jing'an", "Putuo", "Hongkou", "Yangpu", "Minhang",
            "Baoshan", "Jiading", "Pudong", "Jinshan", "Songjiang", "Qingpu", "Fengxian", "Chongming"
        ],
        "Jiangsu": [
            "Nanjing", "Suzhou", "Wuxi", "Changzhou", "Nantong", "Xuzhou", "Yancheng", "Yangzhou",
            "Taizhou", "Zhenjiang", "Huai'an", "Lianyungang", "Suqian", "Kunshan", "Jiangyin",
            "Zhangjiagang", "Changshu", "Taicang", "Yixing", "Danyang", "Jurong", "Haimen"
        ]
    },
    
    "AU": {  # Australia
        "New South Wales": [
            "Sydney", "Newcastle", "Wollongong", "Central Coast", "Maitland", "Albury", "Wagga Wagga",
            "Port Macquarie", "Tamworth", "Orange", "Dubbo", "Queanbeyan", "Bathurst", "Nowra",
            "Griffith", "Lismore", "Armidale", "Broken Hill", "Goulburn", "Mudgee", "Young", "Parkes"
        ],
        "Victoria": [
            "Melbourne", "Geelong", "Ballarat", "Bendigo", "Frankston", "Mildura", "Shepparton",
            "Wodonga", "Warrnambool", "Traralgon", "Horsham", "Sale", "Echuca", "Wangaratta",
            "Swan Hill", "Bairnsdale", "Colac", "Hamilton", "Portland", "Ararat", "Stawell"
        ],
        "Queensland": [
            "Brisbane", "Gold Coast", "Townsville", "Cairns", "Toowoomba", "Mackay", "Rockhampton",
            "Bundaberg", "Hervey Bay", "Gladstone", "Mount Isa", "Maryborough", "Ipswich", "Logan",
            "Redland", "Moreton Bay", "Sunshine Coast", "Warwick", "Roma", "Charleville", "Longreach"
        ]
    },
    
    "MX": {  # Mexico
        "Mexico City": [
            "Mexico City", "Iztapalapa", "Gustavo A. Madero", "Álvaro Obregón", "Tlalpan",
            "Coyoacán", "Venustiano Carranza", "Azcapotzalco", "Xochimilco", "Benito Juárez",
            "Miguel Hidalgo", "Iztacalco", "Cuauhtémoc", "Tláhuac", "La Magdalena Contreras",
            "Milpa Alta", "Cuajimalpa"
        ],
        "Jalisco": [
            "Guadalajara", "Zapopan", "Tlaquepaque", "Tonalá", "Puerto Vallarta", "Tlajomulco de Zúñiga",
            "El Salto", "Tepatitlán", "Lagos de Moreno", "Ocotlán", "Ciudad Guzmán", "Arandas",
            "La Barca", "Ameca", "Autlán", "Chapala", "Tequila", "Sayula", "Tapalpa", "Mascota"
        ],
        "Nuevo León": [
            "Monterrey", "Guadalupe", "San Nicolás de los Garza", "Apodaca", "General Escobedo",
            "Santa Catarina", "San Pedro Garza García", "Juárez", "Cadereyta Jiménez", "García",
            "El Carmen", "Pesquería", "Ciénega de Flores", "Salinas Victoria", "Santiago"
        ]
    }
}

def get_cities_for_state(country_code, state_name):
    """Get cities for a specific country and state"""
    country_data = CITIES_DATA.get(country_code.upper(), {})
    return country_data.get(state_name, [])

def get_all_cities_for_country(country_code):
    """Get all cities for a country across all states"""
    country_data = CITIES_DATA.get(country_code.upper(), {})
    all_cities = []
    for state_cities in country_data.values():
        all_cities.extend(state_cities)
    return sorted(set(all_cities))

def search_cities(query, country_code=None, state_name=None):
    """Search cities by query with optional country/state filtering"""
    query = query.lower()
    results = []
    
    if country_code and state_name:
        # Search within specific state
        cities = get_cities_for_state(country_code, state_name)
        results = [city for city in cities if query in city.lower()]
    elif country_code:
        # Search within specific country
        cities = get_all_cities_for_country(country_code)
        results = [city for city in cities if query in city.lower()]
    else:
        # Search globally
        for cc, country_data in CITIES_DATA.items():
            for state, cities in country_data.items():
                matching_cities = [city for city in cities if query in city.lower()]
                for city in matching_cities:
                    results.append({
                        "city": city,
                        "state": state,
                        "country_code": cc
                    })
    
    return results[:50]  # Limit results