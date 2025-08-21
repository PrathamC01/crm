"""
Comprehensive Geographic Data Mapping
Complete countries, states/provinces, and major cities database
"""

# Complete ISO 3166-1 alpha-2 country codes with names
COUNTRIES = [
    {"code": "AD", "name": "Andorra"},
    {"code": "AE", "name": "United Arab Emirates"},
    {"code": "AF", "name": "Afghanistan"},
    {"code": "AG", "name": "Antigua and Barbuda"},
    {"code": "AI", "name": "Anguilla"},
    {"code": "AL", "name": "Albania"},
    {"code": "AM", "name": "Armenia"},
    {"code": "AO", "name": "Angola"},
    {"code": "AQ", "name": "Antarctica"},
    {"code": "AR", "name": "Argentina"},
    {"code": "AS", "name": "American Samoa"},
    {"code": "AT", "name": "Austria"},
    {"code": "AU", "name": "Australia"},
    {"code": "AW", "name": "Aruba"},
    {"code": "AX", "name": "Åland Islands"},
    {"code": "AZ", "name": "Azerbaijan"},
    {"code": "BA", "name": "Bosnia and Herzegovina"},
    {"code": "BB", "name": "Barbados"},
    {"code": "BD", "name": "Bangladesh"},
    {"code": "BE", "name": "Belgium"},
    {"code": "BF", "name": "Burkina Faso"},
    {"code": "BG", "name": "Bulgaria"},
    {"code": "BH", "name": "Bahrain"},
    {"code": "BI", "name": "Burundi"},
    {"code": "BJ", "name": "Benin"},
    {"code": "BL", "name": "Saint Barthélemy"},
    {"code": "BM", "name": "Bermuda"},
    {"code": "BN", "name": "Brunei Darussalam"},
    {"code": "BO", "name": "Bolivia"},
    {"code": "BQ", "name": "Bonaire, Sint Eustatius and Saba"},
    {"code": "BR", "name": "Brazil"},
    {"code": "BS", "name": "Bahamas"},
    {"code": "BT", "name": "Bhutan"},
    {"code": "BV", "name": "Bouvet Island"},
    {"code": "BW", "name": "Botswana"},
    {"code": "BY", "name": "Belarus"},
    {"code": "BZ", "name": "Belize"},
    {"code": "CA", "name": "Canada"},
    {"code": "CC", "name": "Cocos (Keeling) Islands"},
    {"code": "CD", "name": "Congo, Democratic Republic of the"},
    {"code": "CF", "name": "Central African Republic"},
    {"code": "CG", "name": "Congo"},
    {"code": "CH", "name": "Switzerland"},
    {"code": "CI", "name": "Côte d'Ivoire"},
    {"code": "CK", "name": "Cook Islands"},
    {"code": "CL", "name": "Chile"},
    {"code": "CM", "name": "Cameroon"},
    {"code": "CN", "name": "China"},
    {"code": "CO", "name": "Colombia"},
    {"code": "CR", "name": "Costa Rica"},
    {"code": "CU", "name": "Cuba"},
    {"code": "CV", "name": "Cabo Verde"},
    {"code": "CW", "name": "Curaçao"},
    {"code": "CX", "name": "Christmas Island"},
    {"code": "CY", "name": "Cyprus"},
    {"code": "CZ", "name": "Czech Republic"},
    {"code": "DE", "name": "Germany"},
    {"code": "DJ", "name": "Djibouti"},
    {"code": "DK", "name": "Denmark"},
    {"code": "DM", "name": "Dominica"},
    {"code": "DO", "name": "Dominican Republic"},
    {"code": "DZ", "name": "Algeria"},
    {"code": "EC", "name": "Ecuador"},
    {"code": "EE", "name": "Estonia"},
    {"code": "EG", "name": "Egypt"},
    {"code": "EH", "name": "Western Sahara"},
    {"code": "ER", "name": "Eritrea"},
    {"code": "ES", "name": "Spain"},
    {"code": "ET", "name": "Ethiopia"},
    {"code": "FI", "name": "Finland"},
    {"code": "FJ", "name": "Fiji"},
    {"code": "FK", "name": "Falkland Islands (Malvinas)"},
    {"code": "FM", "name": "Micronesia, Federated States of"},
    {"code": "FO", "name": "Faroe Islands"},
    {"code": "FR", "name": "France"},
    {"code": "GA", "name": "Gabon"},
    {"code": "GB", "name": "United Kingdom"},
    {"code": "GD", "name": "Grenada"},
    {"code": "GE", "name": "Georgia"},
    {"code": "GF", "name": "French Guiana"},
    {"code": "GG", "name": "Guernsey"},
    {"code": "GH", "name": "Ghana"},
    {"code": "GI", "name": "Gibraltar"},
    {"code": "GL", "name": "Greenland"},
    {"code": "GM", "name": "Gambia"},
    {"code": "GN", "name": "Guinea"},
    {"code": "GP", "name": "Guadeloupe"},
    {"code": "GQ", "name": "Equatorial Guinea"},
    {"code": "GR", "name": "Greece"},
    {"code": "GS", "name": "South Georgia and the South Sandwich Islands"},
    {"code": "GT", "name": "Guatemala"},
    {"code": "GU", "name": "Guam"},
    {"code": "GW", "name": "Guinea-Bissau"},
    {"code": "GY", "name": "Guyana"},
    {"code": "HK", "name": "Hong Kong"},
    {"code": "HM", "name": "Heard Island and McDonald Islands"},
    {"code": "HN", "name": "Honduras"},
    {"code": "HR", "name": "Croatia"},
    {"code": "HT", "name": "Haiti"},
    {"code": "HU", "name": "Hungary"},
    {"code": "ID", "name": "Indonesia"},
    {"code": "IE", "name": "Ireland"},
    {"code": "IL", "name": "Israel"},
    {"code": "IM", "name": "Isle of Man"},
    {"code": "IN", "name": "India"},
    {"code": "IO", "name": "British Indian Ocean Territory"},
    {"code": "IQ", "name": "Iraq"},
    {"code": "IR", "name": "Iran, Islamic Republic of"},
    {"code": "IS", "name": "Iceland"},
    {"code": "IT", "name": "Italy"},
    {"code": "JE", "name": "Jersey"},
    {"code": "JM", "name": "Jamaica"},
    {"code": "JO", "name": "Jordan"},
    {"code": "JP", "name": "Japan"},
    {"code": "KE", "name": "Kenya"},
    {"code": "KG", "name": "Kyrgyzstan"},
    {"code": "KH", "name": "Cambodia"},
    {"code": "KI", "name": "Kiribati"},
    {"code": "KM", "name": "Comoros"},
    {"code": "KN", "name": "Saint Kitts and Nevis"},
    {"code": "KP", "name": "Korea, Democratic People's Republic of"},
    {"code": "KR", "name": "Korea, Republic of"},
    {"code": "KW", "name": "Kuwait"},
    {"code": "KY", "name": "Cayman Islands"},
    {"code": "KZ", "name": "Kazakhstan"},
    {"code": "LA", "name": "Lao People's Democratic Republic"},
    {"code": "LB", "name": "Lebanon"},
    {"code": "LC", "name": "Saint Lucia"},
    {"code": "LI", "name": "Liechtenstein"},
    {"code": "LK", "name": "Sri Lanka"},
    {"code": "LR", "name": "Liberia"},
    {"code": "LS", "name": "Lesotho"},
    {"code": "LT", "name": "Lithuania"},
    {"code": "LU", "name": "Luxembourg"},
    {"code": "LV", "name": "Latvia"},
    {"code": "LY", "name": "Libya"},
    {"code": "MA", "name": "Morocco"},
    {"code": "MC", "name": "Monaco"},
    {"code": "MD", "name": "Moldova, Republic of"},
    {"code": "ME", "name": "Montenegro"},
    {"code": "MF", "name": "Saint Martin (French part)"},
    {"code": "MG", "name": "Madagascar"},
    {"code": "MH", "name": "Marshall Islands"},
    {"code": "MK", "name": "North Macedonia"},
    {"code": "ML", "name": "Mali"},
    {"code": "MM", "name": "Myanmar"},
    {"code": "MN", "name": "Mongolia"},
    {"code": "MO", "name": "Macao"},
    {"code": "MP", "name": "Northern Mariana Islands"},
    {"code": "MQ", "name": "Martinique"},
    {"code": "MR", "name": "Mauritania"},
    {"code": "MS", "name": "Montserrat"},
    {"code": "MT", "name": "Malta"},
    {"code": "MU", "name": "Mauritius"},
    {"code": "MV", "name": "Maldives"},
    {"code": "MW", "name": "Malawi"},
    {"code": "MX", "name": "Mexico"},
    {"code": "MY", "name": "Malaysia"},
    {"code": "MZ", "name": "Mozambique"},
    {"code": "NA", "name": "Namibia"},
    {"code": "NC", "name": "New Caledonia"},
    {"code": "NE", "name": "Niger"},
    {"code": "NF", "name": "Norfolk Island"},
    {"code": "NG", "name": "Nigeria"},
    {"code": "NI", "name": "Nicaragua"},
    {"code": "NL", "name": "Netherlands"},
    {"code": "NO", "name": "Norway"},
    {"code": "NP", "name": "Nepal"},
    {"code": "NR", "name": "Nauru"},
    {"code": "NU", "name": "Niue"},
    {"code": "NZ", "name": "New Zealand"},
    {"code": "OM", "name": "Oman"},
    {"code": "PA", "name": "Panama"},
    {"code": "PE", "name": "Peru"},
    {"code": "PF", "name": "French Polynesia"},
    {"code": "PG", "name": "Papua New Guinea"},
    {"code": "PH", "name": "Philippines"},
    {"code": "PK", "name": "Pakistan"},
    {"code": "PL", "name": "Poland"},
    {"code": "PM", "name": "Saint Pierre and Miquelon"},
    {"code": "PN", "name": "Pitcairn"},
    {"code": "PR", "name": "Puerto Rico"},
    {"code": "PS", "name": "Palestine, State of"},
    {"code": "PT", "name": "Portugal"},
    {"code": "PW", "name": "Palau"},
    {"code": "PY", "name": "Paraguay"},
    {"code": "QA", "name": "Qatar"},
    {"code": "RE", "name": "Réunion"},
    {"code": "RO", "name": "Romania"},
    {"code": "RS", "name": "Serbia"},
    {"code": "RU", "name": "Russian Federation"},
    {"code": "RW", "name": "Rwanda"},
    {"code": "SA", "name": "Saudi Arabia"},
    {"code": "SB", "name": "Solomon Islands"},
    {"code": "SC", "name": "Seychelles"},
    {"code": "SD", "name": "Sudan"},
    {"code": "SE", "name": "Sweden"},
    {"code": "SG", "name": "Singapore"},
    {"code": "SH", "name": "Saint Helena, Ascension and Tristan da Cunha"},
    {"code": "SI", "name": "Slovenia"},
    {"code": "SJ", "name": "Svalbard and Jan Mayen"},
    {"code": "SK", "name": "Slovakia"},
    {"code": "SL", "name": "Sierra Leone"},
    {"code": "SM", "name": "San Marino"},
    {"code": "SN", "name": "Senegal"},
    {"code": "SO", "name": "Somalia"},
    {"code": "SR", "name": "Suriname"},
    {"code": "SS", "name": "South Sudan"},
    {"code": "ST", "name": "Sao Tome and Principe"},
    {"code": "SV", "name": "El Salvador"},
    {"code": "SX", "name": "Sint Maarten (Dutch part)"},
    {"code": "SY", "name": "Syrian Arab Republic"},
    {"code": "SZ", "name": "Eswatini"},
    {"code": "TC", "name": "Turks and Caicos Islands"},
    {"code": "TD", "name": "Chad"},
    {"code": "TF", "name": "French Southern Territories"},
    {"code": "TG", "name": "Togo"},
    {"code": "TH", "name": "Thailand"},
    {"code": "TJ", "name": "Tajikistan"},
    {"code": "TK", "name": "Tokelau"},
    {"code": "TL", "name": "Timor-Leste"},
    {"code": "TM", "name": "Turkmenistan"},
    {"code": "TN", "name": "Tunisia"},
    {"code": "TO", "name": "Tonga"},
    {"code": "TR", "name": "Turkey"},
    {"code": "TT", "name": "Trinidad and Tobago"},
    {"code": "TV", "name": "Tuvalu"},
    {"code": "TW", "name": "Taiwan, Province of China"},
    {"code": "TZ", "name": "Tanzania, United Republic of"},
    {"code": "UA", "name": "Ukraine"},
    {"code": "UG", "name": "Uganda"},
    {"code": "UM", "name": "United States Minor Outlying Islands"},
    {"code": "US", "name": "United States"},
    {"code": "UY", "name": "Uruguay"},
    {"code": "UZ", "name": "Uzbekistan"},
    {"code": "VA", "name": "Holy See (Vatican City State)"},
    {"code": "VC", "name": "Saint Vincent and the Grenadines"},
    {"code": "VE", "name": "Venezuela, Bolivarian Republic of"},
    {"code": "VG", "name": "Virgin Islands, British"},
    {"code": "VI", "name": "Virgin Islands, U.S."},
    {"code": "VN", "name": "Viet Nam"},
    {"code": "VU", "name": "Vanuatu"},
    {"code": "WF", "name": "Wallis and Futuna"},
    {"code": "WS", "name": "Samoa"},
    {"code": "YE", "name": "Yemen"},
    {"code": "YT", "name": "Mayotte"},
    {"code": "ZA", "name": "South Africa"},
    {"code": "ZM", "name": "Zambia"},
    {"code": "ZW", "name": "Zimbabwe"}
]

# Comprehensive States/Provinces mapping for all major countries
STATES_DATA = {
    "AD": [],  # Andorra - No states/provinces
    
    "AE": [  # United Arab Emirates
        "Abu Dhabi", "Ajman", "Dubai", "Fujairah", "Ras Al Khaimah", "Sharjah", "Umm Al Quwain"
    ],
    
    "AF": [  # Afghanistan
        "Badakhshan", "Badghis", "Baghlan", "Balkh", "Bamyan", "Daykundi", "Farah", "Faryab",
        "Ghazni", "Ghor", "Helmand", "Herat", "Jowzjan", "Kabul", "Kandahar", "Kapisa",
        "Khost", "Kunar", "Kunduz", "Laghman", "Logar", "Nangarhar", "Nimroz", "Nuristan",
        "Paktia", "Paktika", "Panjshir", "Parwan", "Samangan", "Sar-e Pol", "Takhar",
        "Urozgan", "Wardak", "Zabul"
    ],
    
    "AG": [],  # Antigua and Barbuda - No states/provinces
    
    "AL": [  # Albania
        "Berat", "Dibër", "Durrës", "Elbasan", "Fier", "Gjirokastër", "Korçë", "Kukës",
        "Lezhë", "Shkodër", "Tirana", "Vlorë"
    ],
    
    "AM": [  # Armenia
        "Aragatsotn", "Ararat", "Armavir", "Geghark'unik'", "Kotayk'", "Lorri", "Shirak",
        "Syunik'", "Tavush", "Vayots' Dzor", "Yerevan"
    ],
    
    "AO": [  # Angola
        "Bengo", "Benguela", "Bié", "Cabinda", "Cuando Cubango", "Cuanza Norte", "Cuanza Sul",
        "Cunene", "Huambo", "Huíla", "Luanda", "Lunda Norte", "Lunda Sul", "Malanje", "Moxico",
        "Namibe", "Uíge", "Zaire"
    ],
    
    "AR": [  # Argentina
        "Buenos Aires", "Buenos Aires Capital", "Catamarca", "Chaco", "Chubut", "Córdoba", 
        "Corrientes", "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza",
        "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz",
        "Santa Fe", "Santiago del Estero", "Tierra del Fuego", "Tucumán"
    ],
    
    "AT": [  # Austria
        "Burgenland", "Carinthia", "Lower Austria", "Upper Austria", "Salzburg", "Styria",
        "Tyrol", "Vorarlberg", "Vienna"
    ],
    
    "AU": [  # Australia
        "Australian Capital Territory", "New South Wales", "Northern Territory", "Queensland",
        "South Australia", "Tasmania", "Victoria", "Western Australia"
    ],
    
    "AZ": [  # Azerbaijan
        "Absheron", "Agdam", "Agdash", "Agstafa", "Agsu", "Astara", "Baku", "Balakan", "Barda",
        "Beylagan", "Bilasuvar", "Dashkasan", "Fizuli", "Ganja", "Gobustan", "Goranboy",
        "Goychay", "Hajigabul", "Imishli", "Ismailli", "Jabrayil", "Jalilabad", "Kalbajar",
        "Kurdamir", "Lachin", "Lankaran", "Lerik", "Masalli", "Mingachevir", "Naftalan",
        "Nakhchivan", "Neftchala", "Oghuz", "Qabala", "Qakh", "Qazakh", "Quba", "Qubadli",
        "Qusar", "Saatli", "Sabirabad", "Salyan", "Shamakhi", "Shamkir", "Sheki", "Shirvan",
        "Shusha", "Siazan", "Sumgayit", "Tartar", "Tovuz", "Ujar", "Yardimli", "Yevlakh",
        "Zangilan", "Zaqatala", "Zardab"
    ],
    
    "BA": [  # Bosnia and Herzegovina
        "Brčko District", "Federation of Bosnia and Herzegovina", "Republika Srpska"
    ],
    
    "BD": [  # Bangladesh
        "Barishal", "Chattogram", "Dhaka", "Khulna", "Mymensingh", "Rajshahi", "Rangpur", "Sylhet"
    ],
    
    "BE": [  # Belgium
        "Brussels", "Flanders", "Wallonia"
    ],
    
    "BF": [  # Burkina Faso
        "Boucle du Mouhoun", "Cascades", "Centre", "Centre-Est", "Centre-Nord", "Centre-Ouest",
        "Centre-Sud", "Est", "Hauts-Bassins", "Nord", "Plateau-Central", "Sahel", "Sud-Ouest"
    ],
    
    "BG": [  # Bulgaria
        "Blagoevgrad", "Burgas", "Dobrich", "Gabrovo", "Haskovo", "Kardzhali", "Kyustendil",
        "Lovech", "Montana", "Pazardzhik", "Pernik", "Pleven", "Plovdiv", "Razgrad", "Ruse",
        "Shumen", "Silistra", "Sliven", "Smolyan", "Sofia", "Sofia City", "Stara Zagora",
        "Targovishte", "Varna", "Veliko Tarnovo", "Vidin", "Vratsa", "Yambol"
    ],
    
    "BH": [],  # Bahrain - No states/provinces
    
    "BI": [  # Burundi
        "Bubanza", "Bujumbura Mairie", "Bujumbura Rural", "Bururi", "Cankuzo", "Cibitoke",
        "Gitega", "Karuzi", "Kayanza", "Kirundo", "Makamba", "Muramvya", "Muyinga", "Mwaro",
        "Ngozi", "Rumonge", "Rutana", "Ruyigi"
    ],
    
    "BJ": [  # Benin
        "Alibori", "Atakora", "Atlantique", "Borgou", "Collines", "Couffo", "Donga", "Littoral",
        "Mono", "Ouémé", "Plateau", "Zou"
    ],
    
    "BO": [  # Bolivia
        "Beni", "Chuquisaca", "Cochabamba", "La Paz", "Oruro", "Pando", "Potosí", "Santa Cruz", "Tarija"
    ],
    
    "BR": [  # Brazil
        "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal",
        "Espírito Santo", "Goiás", "Maranhão", "Mato Grosso", "Mato Grosso do Sul",
        "Minas Gerais", "Pará", "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro",
        "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", "Roraima", "Santa Catarina",
        "São Paulo", "Sergipe", "Tocantins"
    ],
    
    "BT": [  # Bhutan
        "Bumthang", "Chhukha", "Dagana", "Gasa", "Haa", "Lhuentse", "Mongar", "Paro",
        "Pemagatshel", "Punakha", "Samdrup Jongkhar", "Samtse", "Sarpang", "Thimphu",
        "Trashigang", "Trashiyangtse", "Trongsa", "Tsirang", "Wangdue Phodrang", "Zhemgang"
    ],
    
    "BW": [  # Botswana
        "Central", "Ghanzi", "Kgalagadi", "Kgatleng", "Kweneng", "North East", "North West",
        "South East", "Southern"
    ],
    
    "BY": [  # Belarus
        "Brest", "Gomel", "Grodno", "Minsk", "Minsk City", "Mogilev", "Vitebsk"
    ],
    
    "BZ": [  # Belize
        "Belize", "Cayo", "Corozal", "Orange Walk", "Stann Creek", "Toledo"
    ],
    
    "CA": [  # Canada
        "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
        "Northwest Territories", "Nova Scotia", "Nunavut", "Ontario", "Prince Edward Island",
        "Quebec", "Saskatchewan", "Yukon"
    ],
    
    "CD": [  # Congo, Democratic Republic of the
        "Bas-Uele", "Equateur", "Haut-Katanga", "Haut-Lomami", "Haut-Uele", "Ituri", "Kasai",
        "Kasai-Central", "Kasai-Oriental", "Kinshasa", "Kongo-Central", "Kwango", "Kwilu",
        "Lomami", "Lualaba", "Mai-Ndombe", "Maniema", "Mongala", "Nord-Kivu", "Nord-Ubangi",
        "Sankuru", "Sud-Kivu", "Sud-Ubangi", "Tanganyika", "Tshopo", "Tshuapa"
    ],
    
    "CF": [  # Central African Republic
        "Bamingui-Bangoran", "Bangui", "Basse-Kotto", "Haute-Kotto", "Haut-Mbomou", "Kémo",
        "Lobaye", "Mambéré-Kadéï", "Mbomou", "Nana-Grébizi", "Nana-Mambéré", "Ombella-M'Poko",
        "Ouaka", "Ouham", "Ouham-Pendé", "Sangha-Mbaéré", "Vakaga"
    ],
    
    "CG": [  # Congo
        "Bouenza", "Brazzaville", "Cuvette", "Cuvette-Ouest", "Kouilou", "Lékoumou", "Likouala",
        "Niari", "Plateaux", "Pointe-Noire", "Pool", "Sangha"
    ],
    
    "CH": [  # Switzerland
        "Aargau", "Appenzell Ausserrhoden", "Appenzell Innerrhoden", "Basel-Landschaft",
        "Basel-Stadt", "Bern", "Fribourg", "Geneva", "Glarus", "Graubünden", "Jura", "Lucerne",
        "Neuchâtel", "Nidwalden", "Obwalden", "Schaffhausen", "Schwyz", "Solothurn",
        "St. Gallen", "Thurgau", "Ticino", "Uri", "Valais", "Vaud", "Zug", "Zürich"
    ],
    
    "CI": [  # Côte d'Ivoire
        "Agnéby-Tiassa", "Bafing", "Bagoué", "Béré", "Bounkani", "Cavally", "Folon",
        "Gbêkê", "Gbôklé", "Gôh", "Gontougo", "Grands-Ponts", "Guémon", "Hambol", "Haut-Sassandra",
        "Iffou", "Indénié-Djuablin", "Kabadougou", "Lôh-Djiboua", "Marahoué", "Moronou",
        "N'Zi", "Nawa", "Poro", "San-Pédro", "Tchologo", "Tonkpi", "Worodougou"
    ],
    
    "CL": [  # Chile
        "Arica y Parinacota", "Tarapacá", "Antofagasta", "Atacama", "Coquimbo", "Valparaíso",
        "Metropolitana de Santiago", "O'Higgins", "Maule", "Ñuble", "Biobío", "La Araucanía",
        "Los Ríos", "Los Lagos", "Aysén", "Magallanes y la Antártica Chilena"
    ],
    
    "CM": [  # Cameroon
        "Adamaoua", "Centre", "East", "Far North", "Littoral", "North", "North-West",
        "South", "South-West", "West"
    ],
    
    "CN": [  # China
        "Anhui", "Beijing", "Chongqing", "Fujian", "Gansu", "Guangdong", "Guangxi", "Guizhou",
        "Hainan", "Hebei", "Heilongjiang", "Henan", "Hong Kong", "Hubei", "Hunan", "Inner Mongolia",
        "Jiangsu", "Jiangxi", "Jilin", "Liaoning", "Macao", "Ningxia", "Qinghai", "Shaanxi",
        "Shandong", "Shanghai", "Shanxi", "Sichuan", "Taiwan", "Tianjin", "Tibet", "Xinjiang",
        "Yunnan", "Zhejiang"
    ],
    
    "CO": [  # Colombia
        "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bolívar", "Boyacá", "Caldas", "Caquetá",
        "Casanare", "Cauca", "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía", "Guaviare",
        "Huila", "La Guajira", "Magdalena", "Meta", "Nariño", "Norte de Santander", "Putumayo",
        "Quindío", "Risaralda", "San Andrés y Providencia", "Santander", "Sucre", "Tolima",
        "Valle del Cauca", "Vaupés", "Vichada", "Bogotá D.C."
    ],
    
    "CR": [  # Costa Rica
        "Alajuela", "Cartago", "Guanacaste", "Heredia", "Limón", "Puntarenas", "San José"
    ],
    
    "CU": [  # Cuba
        "Artemisa", "Camagüey", "Ciego de Ávila", "Cienfuegos", "Granma", "Guantánamo",
        "Havana", "Holguín", "Isla de la Juventud", "Las Tunas", "Matanzas", "Mayabeque",
        "Pinar del Río", "Sancti Spíritus", "Santiago de Cuba", "Villa Clara"
    ],
    
    "CV": [  # Cabo Verde
        "Barlavento", "Sotavento"
    ],
    
    "CY": [  # Cyprus
        "Famagusta", "Kyrenia", "Larnaca", "Limassol", "Nicosia", "Paphos"
    ],
    
    "CZ": [  # Czech Republic
        "Central Bohemian", "Hradec Králové", "Karlovy Vary", "Liberec", "Moravian-Silesian",
        "Olomouc", "Pardubice", "Plzeň", "Prague", "South Bohemian", "South Moravian",
        "Ústí nad Labem", "Vysočina", "Zlín"
    ],
    
    "DE": [  # Germany
        "Baden-Württemberg", "Bavaria", "Berlin", "Brandenburg", "Bremen", "Hamburg",
        "Hesse", "Lower Saxony", "Mecklenburg-Vorpommern", "North Rhine-Westphalia",
        "Rhineland-Palatinate", "Saarland", "Saxony", "Saxony-Anhalt", "Schleswig-Holstein",
        "Thuringia"
    ],
    
    "DJ": [  # Djibouti
        "Ali Sabieh", "Arta", "Dikhil", "Djibouti", "Obock", "Tadjourah"
    ],
    
    "DK": [  # Denmark
        "Capital Region", "Central Denmark", "North Denmark", "Region Zealand", "Southern Denmark"
    ],
    
    "DO": [  # Dominican Republic
        "Azua", "Bahoruco", "Barahona", "Dajabón", "Distrito Nacional", "Duarte", "El Seibo",
        "Elías Piña", "Espaillat", "Hato Mayor", "Hermanas Mirabal", "Independencia",
        "La Altagracia", "La Romana", "La Vega", "María Trinidad Sánchez", "Monseñor Nouel",
        "Monte Cristi", "Monte Plata", "Pedernales", "Peravia", "Puerto Plata", "Samaná",
        "San Cristóbal", "San José de Ocoa", "San Juan", "San Pedro de Macorís", "Sánchez Ramírez",
        "Santiago", "Santiago Rodríguez", "Santo Domingo", "Valverde"
    ],
    
    "DZ": [  # Algeria
        "Adrar", "Aïn Defla", "Aïn Témouchent", "Algiers", "Annaba", "Batna", "Béchar",
        "Béjaïa", "Biskra", "Blida", "Bordj Bou Arréridj", "Bouira", "Boumerdès", "Chlef",
        "Constantine", "Djelfa", "El Bayadh", "El Oued", "El Tarf", "Ghardaïa", "Guelma",
        "Illizi", "Jijel", "Khenchela", "Laghouat", "Mascara", "Médéa", "Mila", "Mostaganem",
        "M'Sila", "Naama", "Oran", "Ouargla", "Oum el Bouaghi", "Relizane", "Saïda",
        "Sétif", "Sidi Bel Abbès", "Skikda", "Souk Ahras", "Tamanrasset", "Tébessa",
        "Tiaret", "Tindouf", "Tipaza", "Tissemsilt", "Tizi Ouzou", "Tlemcen"
    ],
    
    "EC": [  # Ecuador
        "Azuay", "Bolívar", "Cañar", "Carchi", "Chimborazo", "Cotopaxi", "El Oro", "Esmeraldas",
        "Galápagos", "Guayas", "Imbabura", "Loja", "Los Ríos", "Manabí", "Morona Santiago",
        "Napo", "Orellana", "Pastaza", "Pichincha", "Santa Elena", "Santo Domingo de los Tsáchilas",
        "Sucumbíos", "Tungurahua", "Zamora-Chinchipe"
    ],
    
    "EE": [  # Estonia
        "Harju", "Hiiu", "Ida-Viru", "Jõgeva", "Järva", "Lääne", "Lääne-Viru", "Põlva",
        "Pärnu", "Rapla", "Saare", "Tartu", "Valga", "Viljandi", "Võru"
    ],
    
    "EG": [  # Egypt
        "Alexandria", "Assiut", "Aswan", "Beheira", "Beni Suef", "Cairo", "Dakahlia", "Damietta",
        "Fayyum", "Gharbia", "Giza", "Ismailia", "Kafr el-Sheikh", "Luxor", "Matruh", "Minya",
        "Monufia", "New Valley", "North Sinai", "Port Said", "Qalyubia", "Qena", "Red Sea",
        "Sharqia", "Sohag", "South Sinai", "Suez"
    ],
    
    "ER": [  # Eritrea
        "Anseba", "Debub", "Debubawi K'eyih Bahri", "Gash-Barka", "Ma'akel", "Semenawi K'eyih Bahri"
    ],
    
    "ES": [  # Spain
        "Andalusia", "Aragon", "Asturias", "Balearic Islands", "Basque Country", "Canary Islands",
        "Cantabria", "Castile and León", "Castile-La Mancha", "Catalonia", "Ceuta", "Extremadura",
        "Galicia", "La Rioja", "Madrid", "Melilla", "Murcia", "Navarre", "Valencia"
    ],
    
    "ET": [  # Ethiopia
        "Addis Ababa", "Afar", "Amhara", "Benishangul-Gumuz", "Dire Dawa", "Gambela", "Harari",
        "Oromia", "Sidama", "Somali", "Southern Nations, Nationalities, and Peoples'", "Tigray"
    ],
    
    "FI": [  # Finland
        "Åland", "Central Finland", "Central Ostrobothnia", "Kainuu", "Kanta-Häme", "Karelia",
        "Kymenlaakso", "Lapland", "North Karelia", "Northern Ostrobothnia", "Northern Savonia",
        "Ostrobothnia", "Päijät-Häme", "Pirkanmaa", "Satakunta", "South Karelia", "Southern Ostrobothnia",
        "Southern Savonia", "Tavastia Proper", "Uusimaa", "Varsinais-Suomi"
    ],
    
    "FJ": [  # Fiji
        "Ba", "Bua", "Cakaudrove", "Kadavu", "Lau", "Lomaiviti", "Macuata", "Nadroga-Navosa",
        "Naitasiri", "Namosi", "Ra", "Rewa", "Serua", "Tailevu"
    ],
    
    "FR": [  # France
        "Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Brittany", "Centre-Val de Loire",
        "Corsica", "Grand Est", "Hauts-de-France", "Île-de-France", "Normandy", "Nouvelle-Aquitaine",
        "Occitanie", "Pays de la Loire", "Provence-Alpes-Côte d'Azur"
    ],
    
    "GA": [  # Gabon
        "Estuaire", "Haut-Ogooué", "Moyen-Ogooué", "Ngounié", "Nyanga", "Ogooué-Ivindo",
        "Ogooué-Lolo", "Ogooué-Maritime", "Woleu-Ntem"
    ],
    
    "GB": [  # United Kingdom
        "England", "Northern Ireland", "Scotland", "Wales"
    ],
    
    "GE": [  # Georgia
        "Adjara", "Guria", "Imereti", "Kakheti", "Kvemo Kartli", "Mtskheta-Mtianeti",
        "Racha-Lechkhumi and Kvemo Svaneti", "Samegrelo-Zemo Svaneti", "Samtskhe-Javakheti",
        "Shida Kartli", "Tbilisi"
    ],
    
    "GH": [  # Ghana
        "Ahafo", "Ashanti", "Bono", "Bono East", "Central", "Eastern", "Greater Accra",
        "North East", "Northern", "Oti", "Savannah", "Upper East", "Upper West", "Volta",
        "Western", "Western North"
    ],
    
    "GM": [  # Gambia
        "Banjul", "Central River", "Lower River", "North Bank", "Upper River", "West Coast"
    ],
    
    "GN": [  # Guinea
        "Beyla", "Boffa", "Boké", "Conakry", "Coyah", "Dabola", "Dalaba", "Dinguiraye",
        "Dubréka", "Faranah", "Forécariah", "Fria", "Gaoual", "Guéckédou", "Kankan",
        "Kérouané", "Kindia", "Kissidougou", "Koubia", "Koundara", "Kouroussa", "Labe",
        "Lélouma", "Lola", "Macenta", "Mali", "Mamou", "Mandiana", "Nzérékoré", "Pita",
        "Siguiri", "Télimélé", "Tougué", "Yomou"
    ],
    
    "GQ": [  # Equatorial Guinea
        "Annobón", "Bioko Norte", "Bioko Sur", "Centro Sur", "Kié-Ntem", "Litoral", "Wele-Nzas"
    ],
    
    "GR": [  # Greece
        "Attica", "Central Greece", "Central Macedonia", "Crete", "East Macedonia and Thrace",
        "Epirus", "Ionian Islands", "North Aegean", "Peloponnese", "South Aegean", "Thessaly",
        "West Greece", "West Macedonia"
    ],
    
    "GT": [  # Guatemala
        "Alta Verapaz", "Baja Verapaz", "Chimaltenango", "Chiquimula", "El Progreso", "Escuintla",
        "Guatemala", "Huehuetenango", "Izabal", "Jalapa", "Jutiapa", "Petén", "Quetzaltenango",
        "Quiché", "Retalhuleu", "Sacatepéquez", "San Marcos", "Santa Rosa", "Sololá", "Suchitepéquez",
        "Totonicapán", "Zacapa"
    ],
    
    "GW": [  # Guinea-Bissau
        "Bafatá", "Biombo", "Bissau", "Bolama", "Cacheu", "Gabú", "Oio", "Quinara", "Tombali"
    ],
    
    "GY": [  # Guyana
        "Barima-Waini", "Cuyuni-Mazaruni", "Demerara-Mahaica", "East Berbice-Corentyne",
        "Essequibo Islands-West Demerara", "Mahaica-Berbice", "Pomeroon-Supenaam",
        "Potaro-Siparuni", "Upper Demerara-Berbice", "Upper Takutu-Upper Essequibo"
    ],
    
    "HN": [  # Honduras
        "Atlántida", "Choluteca", "Colón", "Comayagua", "Copán", "Cortés", "El Paraíso",
        "Francisco Morazán", "Gracias a Dios", "Intibucá", "Islas de la Bahía", "La Paz",
        "Lempira", "Ocotepeque", "Olancho", "Santa Bárbara", "Valle", "Yoro"
    ],
    
    "HR": [  # Croatia
        "Bjelovar-Bilogora", "Brodsko-posavska", "Dubrovnik-Neretva", "Istria", "Karlovac",
        "Koprivnica-Križevci", "Krapina-Zagorje", "Lika-Senj", "Međimurje", "Osijek-Baranja",
        "Požega-Slavonia", "Primorje-Gorski Kotar", "Šibenik-Knin", "Sisak-Moslavina",
        "Split-Dalmatia", "Varaždin", "Virovitica-Podravina", "Vukovar-Srijem", "Zadar",
        "Zagreb", "Zagreb County"
    ],
    
    "HT": [  # Haiti
        "Artibonite", "Centre", "Grand'Anse", "Nippes", "Nord", "Nord-Est", "Nord-Ouest",
        "Ouest", "Sud", "Sud-Est"
    ],
    
    "HU": [  # Hungary
        "Bács-Kiskun", "Baranya", "Békés", "Borsod-Abaúj-Zemplén", "Budapest", "Csongrád-Csanád",
        "Fejér", "Győr-Moson-Sopron", "Hajdú-Bihar", "Heves", "Jász-Nagykun-Szolnok",
        "Komárom-Esztergom", "Nógrád", "Pest", "Somogy", "Szabolcs-Szatmár-Bereg", "Tolna",
        "Vas", "Veszprém", "Zala"
    ],
    
    "ID": [  # Indonesia
        "Aceh", "Bali", "Bangka Belitung Islands", "Banten", "Bengkulu", "Central Java",
        "Central Kalimantan", "Central Sulawesi", "East Java", "East Kalimantan", "East Nusa Tenggara",
        "Gorontalo", "Jakarta", "Jambi", "Lampung", "Maluku", "North Kalimantan", "North Maluku",
        "North Sulawesi", "North Sumatra", "Papua", "Riau", "Riau Islands", "South Kalimantan",
        "South Sulawesi", "South Sumatra", "Southeast Sulawesi", "West Java", "West Kalimantan",
        "West Nusa Tenggara", "West Papua", "West Sulawesi", "West Sumatra", "Yogyakarta"
    ],
    
    "IE": [  # Ireland
        "Carlow", "Cavan", "Clare", "Cork", "Donegal", "Dublin", "Galway", "Kerry", "Kildare",
        "Kilkenny", "Laois", "Leitrim", "Limerick", "Longford", "Louth", "Mayo", "Meath",
        "Monaghan", "Offaly", "Roscommon", "Sligo", "Tipperary", "Waterford", "Westmeath",
        "Wexford", "Wicklow"
    ],
    
    "IL": [  # Israel
        "Central", "Haifa", "Jerusalem", "Northern", "Southern", "Tel Aviv"
    ],
    
    "IN": [  # India
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
        "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
        "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    ],
    
    "IQ": [  # Iraq
        "Al Anbar", "Al Basrah", "Al Muthanna", "Al Qadisiyyah", "An Najaf", "Arbil", "As Sulaymaniyyah",
        "Babil", "Baghdad", "Dahuk", "Dhi Qar", "Diyala", "Karbala", "Kirkuk", "Maysan", "Ninawa",
        "Salah ad Din", "Wasit"
    ],
    
    "IR": [  # Iran
        "Alborz", "Ardabil", "Bushehr", "Chaharmahal and Bakhtiari", "East Azerbaijan", "Fars",
        "Gilan", "Golestan", "Hamadan", "Hormozgan", "Ilam", "Isfahan", "Kerman", "Kermanshah",
        "Khuzestan", "Kohgiluyeh and Boyer-Ahmad", "Kurdistan", "Lorestan", "Markazi", "Mazandaran",
        "North Khorasan", "Qazvin", "Qom", "Razavi Khorasan", "Semnan", "Sistan and Baluchestan",
        "South Khorasan", "Tehran", "West Azerbaijan", "Yazd", "Zanjan"
    ],
    
    "IS": [  # Iceland
        "Capital Region", "Eastern Region", "Northeastern Region", "Northwestern Region",
        "Southern Peninsula", "Southern Region", "Western Region", "Westfjords"
    ],
    
    "IT": [  # Italy
        "Abruzzo", "Aosta Valley", "Apulia", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
        "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardy", "Marche", "Molise", "Piedmont",
        "Sardinia", "Sicily", "Trentino-South Tyrol", "Tuscany", "Umbria", "Veneto"
    ],
    
    "JM": [  # Jamaica
        "Clarendon", "Hanover", "Kingston", "Manchester", "Portland", "Saint Andrew", "Saint Ann",
        "Saint Catherine", "Saint Elizabeth", "Saint James", "Saint Mary", "Saint Thomas", "Trelawny", "Westmoreland"
    ],
    
    "JO": [  # Jordan
        "Ajloun", "Amman", "Aqaba", "Balqa", "Irbid", "Jerash", "Karak", "Ma'an", "Madaba",
        "Mafraq", "Tafilah", "Zarqa"
    ],
    
    "JP": [  # Japan
        "Aichi", "Akita", "Aomori", "Chiba", "Ehime", "Fukui", "Fukuoka", "Fukushima", "Gifu",
        "Gunma", "Hiroshima", "Hokkaido", "Hyogo", "Ibaraki", "Ishikawa", "Iwate", "Kagawa",
        "Kagoshima", "Kanagawa", "Kochi", "Kumamoto", "Kyoto", "Mie", "Miyagi", "Miyazaki",
        "Nagano", "Nagasaki", "Nara", "Niigata", "Oita", "Okayama", "Okinawa", "Osaka", "Saga",
        "Saitama", "Shiga", "Shimane", "Shizuoka", "Tochigi", "Tokushima", "Tokyo", "Tottori",
        "Toyama", "Wakayama", "Yamagata", "Yamaguchi", "Yamanashi"
    ],
    
    "KE": [  # Kenya
        "Baringo", "Bomet", "Bungoma", "Busia", "Elgeyo-Marakwet", "Embu", "Garissa", "Homa Bay",
        "Isiolo", "Kajiado", "Kakamega", "Kericho", "Kiambu", "Kilifi", "Kirinyaga", "Kisii",
        "Kisumu", "Kitui", "Kwale", "Laikipia", "Lamu", "Machakos", "Makueni", "Mandera",
        "Marsabit", "Meru", "Migori", "Mombasa", "Murang'a", "Nairobi", "Nakuru", "Nandi",
        "Narok", "Nyamira", "Nyandarua", "Nyeri", "Samburu", "Siaya", "Taita-Taveta", "Tana River",
        "Tharaka-Nithi", "Trans Nzoia", "Turkana", "Uasin Gishu", "Vihiga", "Wajir", "West Pokot"
    ],
    
    "KG": [  # Kyrgyzstan
        "Batken", "Bishkek", "Chuy", "Issyk-Kul", "Jalal-Abad", "Naryn", "Osh", "Talas"
    ],
    
    "KH": [  # Cambodia
        "Banteay Meanchey", "Battambang", "Kampong Cham", "Kampong Chhnang", "Kampong Speu",
        "Kampong Thom", "Kampot", "Kandal", "Kep", "Koh Kong", "Kratie", "Mondulkiri",
        "Oddar Meanchey", "Pailin", "Phnom Penh", "Preah Sihanouk", "Preah Vihear", "Prey Veng",
        "Pursat", "Ratanakiri", "Siem Reap", "Stung Treng", "Svay Rieng", "Takeo", "Tbong Khmum"
    ],
    
    "KM": [  # Comoros
        "Anjouan", "Grande Comore", "Mohéli"
    ],
    
    "KP": [  # North Korea
        "Chagang", "Gangwon", "Hamgyong-bukto", "Hamgyong-namdo", "Hwanghae-bukto", "Hwanghae-namdo",
        "Kangwon", "Pyongan-bukto", "Pyongan-namdo", "Pyongyang", "Ryanggang"
    ],
    
    "KR": [  # South Korea
        "Busan", "Chungcheongbuk-do", "Chungcheongnam-do", "Daegu", "Daejeon", "Gangwon-do",
        "Gwangju", "Gyeonggi-do", "Gyeongsangbuk-do", "Gyeongsangnam-do", "Incheon", "Jeju-do",
        "Jeollabuk-do", "Jeollanam-do", "Sejong", "Seoul", "Ulsan"
    ],
    
    "KW": [  # Kuwait
        "Al Ahmadi", "Al Farwaniyah", "Al Jahra", "Capital", "Hawalli", "Mubarak Al-Kabeer"
    ],
    
    "KZ": [  # Kazakhstan
        "Akmola", "Aktobe", "Almaty", "Almaty City", "Atyrau", "East Kazakhstan", "Karaganda",
        "Kostanay", "Kyzylorda", "Mangystau", "North Kazakhstan", "Nur-Sultan", "Pavlodar",
        "South Kazakhstan", "West Kazakhstan", "Zhambyl"
    ],
    
    "LA": [  # Laos
        "Attapeu", "Bokeo", "Bolikhamsai", "Champasak", "Houaphanh", "Khammouane", "Luang Namtha",
        "Luang Prabang", "Oudomxay", "Phongsaly", "Sainyabuli", "Salavan", "Savannakhet",
        "Sekong", "Vientiane", "Vientiane Capital", "Xaignabouli", "Xiangkhouang"
    ],
    
    "LB": [  # Lebanon
        "Akkar", "Baalbek-Hermel", "Beirut", "Beqaa", "Mount Lebanon", "Nabatieh", "North", "South"
    ],
    
    "LK": [  # Sri Lanka
        "Central Province", "Eastern Province", "North Central Province", "North Western Province",
        "Northern Province", "Sabaragamuwa Province", "Southern Province", "Uva Province", "Western Province"
    ],
    
    "LR": [  # Liberia
        "Bomi", "Bong", "Gbarpolu", "Grand Bassa", "Grand Cape Mount", "Grand Gedeh", "Grand Kru",
        "Lofa", "Margibi", "Maryland", "Montserrado", "Nimba", "River Cess", "River Gee", "Sinoe"
    ],
    
    "LS": [  # Lesotho
        "Berea", "Butha-Buthe", "Leribe", "Mafeteng", "Maseru", "Mohale's Hoek", "Mokhotlong",
        "Qacha's Nek", "Quthing", "Thaba-Tseka"
    ],
    
    "LT": [  # Lithuania
        "Alytus County", "Kaunas County", "Klaipėda County", "Marijampolė County", "Panevėžys County",
        "Šiauliai County", "Tauragė County", "Telšiai County", "Utena County", "Vilnius County"
    ],
    
    "LU": [  # Luxembourg
        "Diekirch", "Grevenmacher", "Luxembourg"
    ],
    
    "LV": [  # Latvia
        "Aizkraukle", "Alūksne", "Balvi", "Bauska", "Cēsis", "Daugavpils", "Dobele", "Gulbene",
        "Jēkabpils", "Jelgava", "Krāslava", "Kuldīga", "Liepāja", "Limbaži", "Ludza", "Madona",
        "Ogre", "Preiļi", "Rēzekne", "Riga", "Saldus", "Talsi", "Tukums", "Valka", "Valmiera", "Ventspils"
    ],
    
    "LY": [  # Libya
        "Al Butnan", "Al Jabal al Akhdar", "Al Jabal al Gharbi", "Al Jifarah", "Al Kufrah",
        "Al Marj", "Al Marqab", "Al Wahat", "An Nuqat al Khams", "Az Zawiyah", "Benghazi",
        "Darnah", "Ghat", "Misratah", "Murzuq", "Nalut", "Sabha", "Surt", "Tripoli", "Wadi al Hayat",
        "Wadi ash Shati'"
    ],
    
    "MA": [  # Morocco
        "Béni Mellal-Khénifra", "Casablanca-Settat", "Dakhla-Oued Ed-Dahab", "Drâa-Tafilalet",
        "Fès-Meknès", "Guelmim-Oued Noun", "Laâyoune-Sakia El Hamra", "Marrakech-Safi",
        "Oriental", "Rabat-Salé-Kénitra", "Souss-Massa", "Tanger-Tétouan-Al Hoceïma"
    ],
    
    "MD": [  # Moldova
        "Anenii Noi", "Basarabeasca", "Briceni", "Cahul", "Cantemir", "Călărași", "Căușeni",
        "Chișinău", "Cimișlia", "Criuleni", "Dondușeni", "Drochia", "Dubăsari", "Edineț",
        "Fălești", "Florești", "Găgăuzia", "Glodeni", "Hîncești", "Ialoveni", "Leova",
        "Nisporeni", "Ocnița", "Orhei", "Rezina", "Rîșcani", "Sîngerei", "Soroca", "Strășeni",
        "Șoldănești", "Ștefan Vodă", "Taraclia", "Telenești", "Transnistria", "Ungheni"
    ],
    
    "MG": [  # Madagascar
        "Antananarivo", "Antsiranana", "Fianarantsoa", "Mahajanga", "Toamasina", "Toliara"
    ],
    
    "ML": [  # Mali
        "Bamako", "Gao", "Kayes", "Kidal", "Koulikoro", "Ménaka", "Mopti", "Ségou", "Sikasso", "Taoudénit"
    ],
    
    "MM": [  # Myanmar
        "Ayeyarwady", "Bago", "Chin", "Kachin", "Kayah", "Kayin", "Magway", "Mandalay", "Mon",
        "Naypyitaw", "Rakhine", "Sagaing", "Shan", "Tanintharyi", "Yangon"
    ],
    
    "MN": [  # Mongolia
        "Arkhangai", "Bayan-Ölgii", "Bayankhongor", "Bulgan", "Darkhan-Uul", "Dornod", "Dornogovi",
        "Dundgovi", "Govi-Altai", "Govisümber", "Khentii", "Khovd", "Khövsgöl", "Ömnögovi",
        "Orkhon", "Övörkhangai", "Selenge", "Sükhbaatar", "Töv", "Ulaanbaatar", "Uvs", "Zavkhan"
    ],
    
    "MR": [  # Mauritania
        "Adrar", "Assaba", "Brakna", "Dakhlet Nouadhibou", "Gorgol", "Guidimaka", "Hodh Ech Chargui",
        "Hodh El Gharbi", "Inchiri", "Nouakchott-Nord", "Nouakchott-Ouest", "Nouakchott-Sud",
        "Tagant", "Tiris Zemmour", "Trarza"
    ],
    
    "MU": [  # Mauritius
        "Black River", "Flacq", "Grand Port", "Moka", "Pamplemousses", "Plaines Wilhems",
        "Port Louis", "Rivière du Rempart", "Savanne", "Agaléga", "Cargados Carajos", "Rodrigues"
    ],
    
    "MV": [  # Maldives
        "Addu", "Alif Alif", "Alif Dhaal", "Baa", "Dhaalu", "Faafu", "Gaafu Alif", "Gaafu Dhaalu",
        "Gnaviyani", "Haa Alif", "Haa Dhaalu", "Kaafu", "Laamu", "Lhaviyani", "Malé", "Meemu",
        "Noonu", "Raa", "Seenu", "Shaviyani", "Thaa", "Vaavu"
    ],
    
    "MW": [  # Malawi
        "Central Region", "Northern Region", "Southern Region"
    ],
    
    "MX": [  # Mexico
        "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas", "Chihuahua",
        "Coahuila", "Colima", "Durango", "Guanajuato", "Guerrero", "Hidalgo", "Jalisco", "Mexico",
        "Mexico City", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla",
        "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas",
        "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas"
    ],
    
    "MY": [  # Malaysia
        "Johor", "Kedah", "Kelantan", "Kuala Lumpur", "Labuan", "Malacca", "Negeri Sembilan",
        "Pahang", "Penang", "Perak", "Perlis", "Putrajaya", "Sabah", "Sarawak", "Selangor", "Terengganu"
    ],
    
    "MZ": [  # Mozambique
        "Cabo Delgado", "Gaza", "Inhambane", "Manica", "Maputo", "Maputo City", "Nampula", "Niassa",
        "Sofala", "Tete", "Zambézia"
    ],
    
    "NA": [  # Namibia
        "Erongo", "Hardap", "Karas", "Kavango East", "Kavango West", "Khomas", "Kunene", "Ohangwena",
        "Omaheke", "Omusati", "Oshana", "Oshikoto", "Otjozondjupa", "Zambezi"
    ],
    
    "NE": [  # Niger
        "Agadez", "Diffa", "Dosso", "Maradi", "Niamey", "Tahoua", "Tillabéri", "Zinder"
    ],
    
    "NG": [  # Nigeria
        "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
        "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Federal Capital Territory",
        "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara",
        "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers",
        "Sokoto", "Taraba", "Yobe", "Zamfara"
    ],
    
    "NI": [  # Nicaragua
        "Boaco", "Carazo", "Chinandega", "Chontales", "Costa Caribe Norte", "Costa Caribe Sur",
        "Estelí", "Granada", "Jinotega", "León", "Madriz", "Managua", "Masaya", "Matagalpa",
        "Nueva Segovia", "Río San Juan", "Rivas"
    ],
    
    "NL": [  # Netherlands
        "Drenthe", "Flevoland", "Friesland", "Gelderland", "Groningen", "Limburg", "North Brabant",
        "North Holland", "Overijssel", "South Holland", "Utrecht", "Zeeland"
    ],
    
    "NO": [  # Norway
        "Agder", "Innlandet", "Møre og Romsdal", "Nordland", "Oslo", "Rogaland", "Troms og Finnmark",
        "Trøndelag", "Vestfold og Telemark", "Vestland", "Viken"
    ],
    
    "NP": [  # Nepal
        "Bagmati", "Gandaki", "Karnali", "Lumbini", "Province No. 1", "Province No. 2", "Sudurpashchim"
    ],
    
    "NZ": [  # New Zealand
        "Auckland", "Bay of Plenty", "Canterbury", "Gisborne", "Hawke's Bay", "Manawatu-Wanganui",
        "Marlborough", "Nelson", "Northland", "Otago", "Southland", "Taranaki", "Tasman",
        "Waikato", "Wellington", "West Coast"
    ],
    
    "OM": [  # Oman
        "Ad Dakhiliyah", "Ad Dhahirah", "Al Batinah North", "Al Batinah South", "Al Buraimi",
        "Al Wusta", "Ash Sharqiyah North", "Ash Sharqiyah South", "Dhofar", "Muscat", "Musandam"
    ],
    
    "PA": [  # Panama
        "Bocas del Toro", "Chiriquí", "Coclé", "Colón", "Darién", "Herrera", "Los Santos",
        "Panamá", "Panamá Oeste", "Veraguas"
    ],
    
    "PE": [  # Peru
        "Amazonas", "Áncash", "Apurímac", "Arequipa", "Ayacucho", "Cajamarca", "Callao", "Cusco",
        "Huancavelica", "Huánuco", "Ica", "Junín", "La Libertad", "Lambayeque", "Lima", "Loreto",
        "Madre de Dios", "Moquegua", "Pasco", "Piura", "Puno", "San Martín", "Tacna", "Tumbes", "Ucayali"
    ],
    
    "PG": [  # Papua New Guinea
        "Bougainville", "Central", "Chimbu", "Eastern Highlands", "East New Britain", "East Sepik",
        "Enga", "Gulf", "Hela", "Jiwaka", "Madang", "Manus", "Milne Bay", "Morobe", "National Capital District",
        "New Ireland", "Northern", "Southern Highlands", "Western", "Western Highlands", "West New Britain", "West Sepik"
    ],
    
    "PH": [  # Philippines
        "Abra", "Agusan del Norte", "Agusan del Sur", "Aklan", "Albay", "Antique", "Apayao",
        "Aurora", "Basilan", "Bataan", "Batanes", "Batangas", "Benguet", "Biliran", "Bohol",
        "Bukidnon", "Bulacan", "Cagayan", "Camarines Norte", "Camarines Sur", "Camiguin",
        "Capiz", "Catanduanes", "Cavite", "Cebu", "Compostela Valley", "Cotabato", "Davao del Norte",
        "Davao del Sur", "Davao Occidental", "Davao Oriental", "Dinagat Islands", "Eastern Samar",
        "Guimaras", "Ifugao", "Ilocos Norte", "Ilocos Sur", "Iloilo", "Isabela", "Kalinga",
        "La Union", "Laguna", "Lanao del Norte", "Lanao del Sur", "Leyte", "Maguindanao",
        "Marinduque", "Masbate", "Metro Manila", "Misamis Occidental", "Misamis Oriental",
        "Mountain Province", "Negros Occidental", "Negros Oriental", "Northern Samar", "Nueva Ecija",
        "Nueva Vizcaya", "Occidental Mindoro", "Oriental Mindoro", "Palawan", "Pampanga",
        "Pangasinan", "Quezon", "Quirino", "Rizal", "Romblon", "Samar", "Sarangani", "Siquijor",
        "Sorsogon", "South Cotabato", "Southern Leyte", "Sultan Kudarat", "Sulu", "Surigao del Norte",
        "Surigao del Sur", "Tarlac", "Tawi-Tawi", "Zambales", "Zamboanga del Norte", "Zamboanga del Sur",
        "Zamboanga Sibugay"
    ],
    
    "PK": [  # Pakistan
        "Azad Kashmir", "Balochistan", "Gilgit-Baltistan", "Islamabad Capital Territory",
        "Khyber Pakhtunkhwa", "Punjab", "Sindh"
    ],
    
    "PL": [  # Poland
        "Greater Poland", "Kuyavian-Pomeranian", "Lesser Poland", "Lodz", "Lower Silesian", "Lublin",
        "Lubusz", "Masovian", "Opole", "Podlaskie", "Pomeranian", "Silesian", "Subcarpathian",
        "Swietokrzyskie", "Warmian-Masurian", "West Pomeranian"
    ],
    
    "PT": [  # Portugal
        "Aveiro", "Açores", "Beja", "Braga", "Bragança", "Castelo Branco", "Coimbra", "Évora",
        "Faro", "Guarda", "Leiria", "Lisboa", "Madeira", "Portalegre", "Porto", "Santarém",
        "Setúbal", "Viana do Castelo", "Vila Real", "Viseu"
    ],
    
    "PY": [  # Paraguay
        "Alto Paraguay", "Alto Paraná", "Amambay", "Asunción", "Boquerón", "Caaguazú", "Caazapá",
        "Canindeyú", "Central", "Concepción", "Cordillera", "Guairá", "Itapúa", "Misiones",
        "Ñeembucú", "Paraguarí", "Presidente Hayes", "San Pedro"
    ],
    
    "QA": [  # Qatar
        "Ad Dawhah", "Al Khor", "Al Rayyan", "Al Wakrah", "Ash Shamal", "Az Za'ayin", "Umm Salal"
    ],
    
    "RO": [  # Romania
        "Alba", "Arad", "Argeș", "Bacău", "Bihor", "Bistrița-Năsăud", "Botoșani", "Brăila",
        "Brașov", "Bucharest", "Buzău", "Călărași", "Caraș-Severin", "Cluj", "Constanța",
        "Covasna", "Dâmbovița", "Dolj", "Galați", "Giurgiu", "Gorj", "Harghita", "Hunedoara",
        "Ialomița", "Iași", "Ilfov", "Maramureș", "Mehedinți", "Mureș", "Neamț", "Olt", "Prahova",
        "Sălaj", "Satu Mare", "Sibiu", "Suceava", "Teleorman", "Timiș", "Tulcea", "Vâlcea",
        "Vaslui", "Vrancea"
    ],
    
    "RS": [  # Serbia
        "Belgrade", "Bor", "Braničevo", "Jablanica", "Kolubara", "Mačva", "Moravica", "Nišava",
        "Pčinja", "Pirot", "Podunavlje", "Pomoravlje", "Rasina", "Raška", "South Bačka",
        "South Banat", "Srem", "Šumadija", "Toplica", "Vojvodina", "West Bačka", "Zaječar", "Zlatibor"
    ],
    
    "RU": [  # Russia (major federal subjects)
        "Adygea", "Altai Krai", "Altai Republic", "Amur Oblast", "Arkhangelsk Oblast", "Astrakhan Oblast",
        "Bashkortostan", "Belgorod Oblast", "Bryansk Oblast", "Buryatia", "Chechen Republic",
        "Chelyabinsk Oblast", "Chukotka", "Chuvash Republic", "Dagestan", "Ingushetia", "Irkutsk Oblast",
        "Ivanovo Oblast", "Jewish Autonomous Oblast", "Kabardino-Balkaria", "Kaliningrad Oblast",
        "Kalmykia", "Kaluga Oblast", "Kamchatka Krai", "Karachay-Cherkessia", "Karelia", "Kemerovo Oblast",
        "Khabarovsk Krai", "Khakassia", "Khanty-Mansi", "Kirov Oblast", "Komi Republic", "Kostroma Oblast",
        "Krasnodar Krai", "Krasnoyarsk Krai", "Kurgan Oblast", "Kursk Oblast", "Leningrad Oblast",
        "Lipetsk Oblast", "Magadan Oblast", "Mari El", "Mordovia", "Moscow", "Moscow Oblast",
        "Murmansk Oblast", "Nenets", "Nizhny Novgorod Oblast", "North Ossetia-Alania", "Novgorod Oblast",
        "Novosibirsk Oblast", "Omsk Oblast", "Orenburg Oblast", "Oryol Oblast", "Penza Oblast",
        "Perm Krai", "Primorsky Krai", "Pskov Oblast", "Rostov Oblast", "Ryazan Oblast",
        "Saint Petersburg", "Sakha Republic", "Sakhalin Oblast", "Samara Oblast", "Saratov Oblast",
        "Smolensk Oblast", "Stavropol Krai", "Sverdlovsk Oblast", "Tambov Oblast", "Tatarstan",
        "Tomsk Oblast", "Tula Oblast", "Tuva Republic", "Tver Oblast", "Tyumen Oblast", "Udmurt Republic",
        "Ulyanovsk Oblast", "Vladimir Oblast", "Volgograd Oblast", "Vologda Oblast", "Voronezh Oblast",
        "Yamalo-Nenets", "Yaroslavl Oblast", "Zabaykalsky Krai"
    ],
    
    "RW": [  # Rwanda
        "Eastern Province", "Kigali", "Northern Province", "Southern Province", "Western Province"
    ],
    
    "SA": [  # Saudi Arabia
        "Al Bahah", "Al Jawf", "Al Madinah", "Al Qasim", "Ar Riyad", "Ash Sharqiyah", "Asir",
        "Hail", "Jazan", "Makkah", "Najran", "Northern Borders", "Tabuk"
    ],
    
    "SD": [  # Sudan
        "Blue Nile", "Central Darfur", "East Darfur", "Gedaref", "Gezira", "Kassala", "Khartoum",
        "North Darfur", "North Kordofan", "Northern", "Red Sea", "River Nile", "Sennar",
        "South Darfur", "South Kordofan", "West Darfur", "West Kordofan", "White Nile"
    ],
    
    "SE": [  # Sweden
        "Blekinge", "Dalarna", "Gävleborg", "Gotland", "Halland", "Jämtland", "Jönköping",
        "Kalmar", "Kronoberg", "Norrbotten", "Örebro", "Östergötland", "Skåne", "Södermanland",
        "Stockholm", "Uppsala", "Värmland", "Västerbotten", "Västernorrland", "Västmanland", "Västra Götaland"
    ],
    
    "SG": [],  # Singapore - City state, no subdivisions
    
    "SI": [  # Slovenia
        "Carinthia", "Carniola", "Coastal–Karst", "Drava", "Gorizia", "Lower Sava", "Mura",
        "Savinja", "Southeast Slovenia", "Upper Carniola", "Central Slovenia", "Littoral–Inner Carniola"
    ],
    
    "SK": [  # Slovakia  
        "Banská Bystrica", "Bratislava", "Košice", "Nitra", "Prešov", "Trenčín", "Trnava", "Žilina"
    ],
    
    "SL": [  # Sierra Leone
        "Eastern Province", "Northern Province", "Southern Province", "Western Area"
    ],
    
    "SN": [  # Senegal
        "Dakar", "Diourbel", "Fatick", "Kaffrine", "Kaolack", "Kédougou", "Kolda", "Louga",
        "Matam", "Saint-Louis", "Sédhiou", "Tambacounda", "Thiès", "Ziguinchor"
    ],
    
    "SO": [  # Somalia
        "Awdal", "Bakool", "Banaadir", "Bari", "Bay", "Galguduud", "Gedo", "Hiiraan", "Jubbada Dhexe",
        "Jubbada Hoose", "Mudug", "Nugaal", "Sanaag", "Shabeellaha Dhexe", "Shabeellaha Hoose",
        "Sool", "Togdheer", "Woqooyi Galbeed"
    ],
    
    "SR": [  # Suriname
        "Brokopondo", "Commewijne", "Coronie", "Marowijne", "Nickerie", "Para", "Paramaribo",
        "Saramacca", "Sipaliwini", "Wanica"
    ],
    
    "SS": [  # South Sudan
        "Central Equatoria", "Eastern Equatoria", "Jonglei", "Lakes", "Northern Bahr el Ghazal",
        "Unity", "Upper Nile", "Warrap", "Western Bahr el Ghazal", "Western Equatoria"
    ],
    
    "SV": [  # El Salvador
        "Ahuachapán", "Cabañas", "Chalatenango", "Cuscatlán", "La Libertad", "La Paz", "La Unión",
        "Morazán", "San Miguel", "San Salvador", "San Vicente", "Santa Ana", "Sonsonate", "Usulután"
    ],
    
    "SY": [  # Syria
        "Aleppo", "Al-Hasakah", "As-Suwayda", "Damascus", "Daraa", "Deir ez-Zor", "Hama", "Homs",
        "Idlib", "Latakia", "Quneitra", "Raqqa", "Rif Dimashq", "Tartus"
    ],
    
    "SZ": [  # Eswatini (Swaziland)
        "Hhohho", "Lubombo", "Manzini", "Shiselweni"
    ],
    
    "TD": [  # Chad
        "Bahr el Gazel", "Batha", "Borkou", "Chari-Baguirmi", "Ennedi-Est", "Ennedi-Ouest",
        "Guéra", "Hadjer-Lamis", "Kanem", "Lac", "Logone Occidental", "Logone Oriental",
        "Mandoul", "Mayo-Kebbi Est", "Mayo-Kebbi Ouest", "Moyen-Chari", "N'Djamena", "Ouaddaï",
        "Salamat", "Sila", "Tandjilé", "Tibesti", "Wadi Fira"
    ],
    
    "TG": [  # Togo
        "Centrale", "Kara", "Maritime", "Plateaux", "Savanes"
    ],
    
    "TH": [  # Thailand
        "Amnat Charoen", "Ang Thong", "Bangkok", "Bueng Kan", "Buri Ram", "Chachoengsao",
        "Chai Nat", "Chaiyaphum", "Chanthaburi", "Chiang Mai", "Chiang Rai", "Chon Buri",
        "Chumphon", "Kalasin", "Kamphaeng Phet", "Kanchanaburi", "Khon Kaen", "Krabi",
        "Lampang", "Lamphun", "Loei", "Lop Buri", "Mae Hong Son", "Maha Sarakham", "Mukdahan",
        "Nakhon Nayok", "Nakhon Pathom", "Nakhon Phanom", "Nakhon Ratchasima", "Nakhon Sawan",
        "Nakhon Si Thammarat", "Nan", "Narathiwat", "Nong Bua Lam Phu", "Nong Khai", "Nonthaburi",
        "Pathum Thani", "Pattani", "Phang Nga", "Phatthalung", "Phayao", "Phetchabun",
        "Phetchaburi", "Phichit", "Phitsanulok", "Phra Nakhon Si Ayutthaya", "Phrae", "Phuket",
        "Prachin Buri", "Prachuap Khiri Khan", "Ranong", "Ratchaburi", "Rayong", "Roi Et",
        "Sa Kaeo", "Sakon Nakhon", "Samut Prakan", "Samut Sakhon", "Samut Songkhram", "Saraburi",
        "Satun", "Sing Buri", "Sisaket", "Songkhla", "Sukhothai", "Suphan Buri", "Surat Thani",
        "Surin", "Tak", "Trang", "Trat", "Ubon Ratchathani", "Udon Thani", "Uthai Thani",
        "Uttaradit", "Yala", "Yasothon"
    ],
    
    "TJ": [  # Tajikistan
        "Dushanbe", "Gorno-Badakhshan", "Khatlon", "Sughd"
    ],
    
    "TM": [  # Turkmenistan
        "Ahal", "Ashgabat", "Balkan", "Daşoguz", "Lebap", "Mary"
    ],
    
    "TN": [  # Tunisia
        "Ariana", "Béja", "Ben Arous", "Bizerte", "Gabès", "Gafsa", "Jendouba", "Kairouan",
        "Kasserine", "Kébili", "Kef", "Mahdia", "Manouba", "Médenine", "Monastir", "Nabeul",
        "Sfax", "Sidi Bouzid", "Siliana", "Sousse", "Tataouine", "Tozeur", "Tunis", "Zaghouan"
    ],
    
    "TR": [  # Turkey
        "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya",
        "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik",
        "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum",
        "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir",
        "Gaziantep", "Giresun", "Gümüşhane", "Hakkâri", "Hatay", "Iğdır", "Isparta", "Istanbul",
        "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale",
        "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa",
        "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize",
        "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ",
        "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"
    ],
    
    "TT": [  # Trinidad and Tobago
        "Arima", "Chaguanas", "Couva-Tabaquite-Talparo", "Diego Martin", "Mayaro-Rio Claro",
        "Penal-Debe", "Point Fortin", "Port of Spain", "Princes Town", "San Fernando",
        "San Juan-Laventille", "Sangre Grande", "Siparia", "Tunapuna-Piarco", "Tobago"
    ],
    
    "TZ": [  # Tanzania
        "Arusha", "Dar es Salaam", "Dodoma", "Geita", "Iringa", "Kagera", "Katavi", "Kigoma",
        "Kilimanjaro", "Lindi", "Manyara", "Mara", "Mbeya", "Morogoro", "Mtwara", "Mwanza",
        "Njombe", "Pemba North", "Pemba South", "Pwani", "Rukwa", "Ruvuma", "Shinyanga",
        "Simiyu", "Singida", "Songwe", "Tabora", "Tanga", "Unguja North", "Unguja South"
    ],
    
    "UA": [  # Ukraine
        "Cherkasy", "Chernihiv", "Chernivtsi", "Crimea", "Dnipropetrovsk", "Donetsk", "Ivano-Frankivsk",
        "Kharkiv", "Kherson", "Khmelnytskyi", "Kiev", "Kiev City", "Kirovohrad", "Luhansk", "Lviv",
        "Mykolaiv", "Odesa", "Poltava", "Rivne", "Sevastopol", "Sumy", "Ternopil", "Vinnytsia",
        "Volyn", "Zakarpattia", "Zaporizhzhia", "Zhytomyr"
    ],
    
    "UG": [  # Uganda
        "Abim", "Adjumani", "Agago", "Alebtong", "Amolatar", "Amudat", "Amuria", "Amuru",
        "Apac", "Arua", "Budaka", "Bududa", "Bugiri", "Buhweju", "Buikwe", "Bukedea",
        "Bukomansimbi", "Bukwa", "Bulambuli", "Buliisa", "Bundibugyo", "Bushenyi", "Busia",
        "Butaleja", "Butambala", "Butebo", "Buvuma", "Buyende", "Dokolo", "Gomba", "Gulu",
        "Ibanda", "Iganga", "Isingiro", "Jinja", "Kaabong", "Kabale", "Kabarole", "Kaberamaido",
        "Kalangala", "Kaliro", "Kampala", "Kamuli", "Kamwenge", "Kanungu", "Kapchorwa", "Kasese",
        "Katakwi", "Kayunga", "Kibaale", "Kiboga", "Kibuku", "Kiruhura", "Kiryandongo", "Kisoro",
        "Kitgum", "Koboko", "Kole", "Kotido", "Kumi", "Kween", "Kyankwanzi", "Kyegegwa",
        "Kyenjojo", "Lamwo", "Lira", "Luuka", "Luwero", "Lwengo", "Lyantonde", "Manafwa",
        "Maracha", "Masaka", "Masindi", "Mayuge", "Mbale", "Mbarara", "Mitooma", "Mityana",
        "Moroto", "Moyo", "Mpigi", "Mubende", "Mukono", "Nakapiripirit", "Nakaseke", "Nakasongola",
        "Namayingo", "Namutumba", "Napak", "Nebbi", "Ngora", "Ntoroko", "Ntungamo", "Nwoya",
        "Otuke", "Oyam", "Pader", "Pallisa", "Rakai", "Rubirizi", "Rukungiri", "Sembabule",
        "Serere", "Sheema", "Sironko", "Soroti", "Tororo", "Wakiso", "Yumbe", "Zombo"
    ],
    
    "US": [  # United States
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
        "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
        "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
        "Wisconsin", "Wyoming", "Washington D.C."
    ],
    
    "UY": [  # Uruguay
        "Artigas", "Canelones", "Cerro Largo", "Colonia", "Durazno", "Flores", "Florida",
        "Lavalleja", "Maldonado", "Montevideo", "Paysandú", "Río Negro", "Rivera", "Rocha",
        "Salto", "San José", "Soriano", "Tacuarembó", "Treinta y Tres"
    ],
    
    "UZ": [  # Uzbekistan
        "Andijan", "Bukhara", "Fergana", "Jizzakh", "Karakalpakstan", "Kashkadarya", "Khorezm",
        "Namangan", "Navoiy", "Qashqadaryo", "Samarkand", "Sirdaryo", "Surkhandarya", "Tashkent",
        "Tashkent City", "Xorazm"
    ],
    
    "VE": [  # Venezuela
        "Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar", "Carabobo", "Cojedes",
        "Delta Amacuro", "Falcón", "Guárico", "Lara", "Mérida", "Miranda", "Monagas", "Nueva Esparta",
        "Portuguesa", "Sucre", "Táchira", "Trujillo", "Vargas", "Yaracuy", "Zulia", "Capital District"
    ],
    
    "VN": [  # Vietnam
        "An Giang", "Bà Rịa–Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh",
        "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", "Cần Thơ",
        "Cao Bằng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai",
        "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang",
        "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng",
        "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận",
        "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị",
        "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa",
        "Thừa Thiên Huế", "Tiền Giang", "TP. Hồ Chí Minh", "Trà Vinh", "Tuyên Quang",
        "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
    ],
    
    "YE": [  # Yemen
        "Abyan", "Aden", "Al Bayda", "Al Dhale'e", "Al Hudaydah", "Al Jawf", "Al Mahrah",
        "Al Maharwah", "Amran", "Dhamar", "Hadhramaut", "Hajjah", "Ibb", "Lahij", "Ma'rib",
        "Raymah", "Sa'dah", "Sana'a", "Sana'a City", "Shabwah", "Socotra", "Taizz"
    ],
    
    "ZA": [  # South Africa
        "Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo", "Mpumalanga",
        "Northern Cape", "North West", "Western Cape"
    ],
    
    "ZM": [  # Zambia
        "Central", "Copperbelt", "Eastern", "Luapula", "Lusaka", "Muchinga", "Northern",
        "North-Western", "Southern", "Western"
    ],
    
    "ZW": [  # Zimbabwe
        "Bulawayo", "Harare", "Manicaland", "Mashonaland Central", "Mashonaland East",
        "Mashonaland West", "Masvingo", "Matabeleland North", "Matabeleland South", "Midlands"
    ]
}

# Add empty lists for countries without state data defined above
for country in COUNTRIES:
    if country["code"] not in STATES_DATA:
        STATES_DATA[country["code"]] = []

def get_countries():
    """Get all countries sorted alphabetically"""
    return sorted(COUNTRIES, key=lambda x: x["name"])

def get_states_for_country(country_code):
    """Get states/provinces for a specific country"""
    return STATES_DATA.get(country_code.upper(), [])

def get_country_by_code(country_code):
    """Get country info by ISO code"""
    for country in COUNTRIES:
        if country["code"].upper() == country_code.upper():
            return country
    return None