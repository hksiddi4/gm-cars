const colorMap = {
  "ROSWELL GREEN METALLIC": "G4Z",
  "BAEGE METALLIC": "BAEGE METALLIC",
  "COPPERTINO METALLIC": "COPPERTINO METALLIC",
  "ABALONE WHITE": "ABALONE WHITE",
  "SEYCHELLES METALLIC": "SEYCHELLES METALLIC",
  "SEEKER METALLIC": "SEEKER METALLIC",
  "KIMONO METALLIC": "KIMONO METALLIC",
  "CHARTREUSE METALLIC": "CHARTREUSE METALLIC",
  "CHARTREUSE MATTE": "CHARTREUSE MATTE",
  "HIGH VOLTAGE TINT": "HIGH VOLTAGE TINT",
  "TACTICAL TINT": "TACTICAL TINT",
  "HYPERSONIC METALLIC": "HYPERSONIC METALLIC",
  "BARB WIRE": "BARB WIRE",
  "BLACK MEETS KETTLE": "BLACK MEETS KETTLE",
  "ACCELERATE YELLOW METALLIC": "GD0",
  "AMPLIFY ORANGE TINTCOAT": "GC5",
  "CORVETTE RACING YELLOW TINTCOAT": "GC6",
  "ARCTIC WHITE": "G8G",
  "ARGENT SILVER METALLIC": "GXD",
  "BLACK DIAMOND TRICOAT": "GLK",
  "BLACK RAVEN": "GBA",
  "BLACK": "GBA",
  "BLADE SILVER METALLIC": "GAN",
  "BLAZE ORANGE METALLIC": "GCF",
  "CACTI GREEN": "GVR",
  "CAFFEINE METALLIC": "G48",
  "CARBON FLASH METALLIC": "GAR",
  "CERAMIC MATRIX GRAY METALLIC": "G9F",
  "COASTAL BLUE METALLIC": "GJV",
  "COMPETITION YELLOW TINTCOAT": "GBK",
  "CRUSH": "G16",
  "CRYSTAL WHITE TRICOAT": "G1W",
  "CYBER YELLOW METALLIC": "GCP",
  "DARK EMERALD FROST": "G7W",
  "DARK MOON METALLIC": "GLU",
  "DEEP SPACE METALLIC": "GAI",
  "ELECTRIC BLUE": "GMO",
  "ELKHART LAKE BLUE METALLIC": "GS7",
  "EVERGREEN METALLIC": "GJ0",
  "GARNET METALLIC": "GLR",
  "GARNET RED TINTCOAT": "G7E",
  "HYPERSONIC GRAY METALLIC": "GA7",
  "HYSTERIA PURPLE METALLIC": "GXL",
  "INFRARED TINTCOAT": "GSK",
  "LONG BEACH RED METALLIC TINTCOAT": "G1E",
  "MANHATTAN NOIR METALLIC": "GCI",
  "MAVERICK NOIR FROST": "GNW",
  "MERCURY SILVER METALLIC": "GKA",
  "MIDNIGHT SKY METALLIC": "GXF",
  "MIDNIGHT STEEL METALLIC": "GXU",
  "NITRO YELLOW METALLIC": "GCP",
  "PANTHER BLACK MATTE": "GNW",
  "PANTHER BLACK METALLIC TINTCOAT": "GLK",
  "RADIANT RED TINTCOAT": "GNT",
  "RADIANT SILVER METALLIC": "GAN",
  "RALLY GREEN METALLIC": "GJ0",
  "RAPID BLUE": "GMO",
  "RED HORIZON TINTCOAT": "GPJ",
  "RED HOT": "G7C",
  "RED MIST METALLIC TINTCOAT": "GPH",
  "RED OBSESSION TINTCOAT": "G7E",
  "RIFT METALLIC": "GRW",
  "RIPTIDE BLUE METALLIC": "GJV",
  "RIVERSIDE BLUE METALLIC": "GKK",
  "ROYAL SPICE METALLIC": "GLL",
  "SATIN STEEL GRAY METALLIC": "G9K",
  "SATIN STEEL METALLIC": "G9K",
  "SEA WOLF GRAY TRICOAT": "GXA",
  "SEBRING ORANGE TINTCOAT": "G26",
  "SHADOW GRAY METALLIC": "GJI",
  "SHADOW METALLIC": "GJI",
  "SHARKSKIN METALLIC": "GXD",
  "SHOCK": "GKO",
  "SILVER FLARE METALLIC": "GSJ",
  "STELLAR BLACK METALLIC": "GB8",
  "SUMMIT WHITE": "GAZ",
  "TORCH RED": "GKZ",
  "TYPHOON METALLIC": "GBW",
  "VELOCITY RED": "G7C",
  "VIVID ORANGE METALLIC": "GCF",
  "WAVE METALLIC": "GKK",
  "WHITE PEARL METALLIC TRICOAT": "G1W",
  "WILD CHERRY TINTCOAT": "GSK",
  "ZEUS BRONZE METALLIC": "GUI",
  "SILVER ICE METALLIC": "GAN",
  "MOSAIC BLACK METALLIC": "GB8",
  "WATKINS GLEN GRAY METALLIC": "G7Q",
  "ADMIRAL BLUE METALLIC": "GTR",
  "INTERSTELLAR WHITE": "GAZ",
  "VOID BLACK": "GBA",
  "METEORITE METALLIC": "GNO",
  "DEEP AURORA METALLIC": "GXN",
  "AFTERBURNER TINTCOAT": "GC5",
  "TIDE METALLIC": "G7X",
  "SUPERNOVA METALLIC": "GKK",
  "NEPTUNE BLUE MATTE": "GLG",
  "SOLAR ORANGE": "GAG",
  "GRAPHITE BLUE METALLIC": "GAI",
  "MOONSHOT GREEN MATTE": "G7W",
  "COASTAL DUNE": "G42",
  "MAGNUS GRAY MATTE": "GBL",
  "AUBURN MATTE": "GNR",
  "BLUE SMOKE METALLIC": "GAI",
  "SLATE GRAY METALLIC": "GNO",
  "HABANERO ORANGE": "GAG",
  "ZEPHYR BLUE MATTE METALLIC": "GLG",
};

const intColor = {
  // Corvette
  // - C7
  "141": "Gray Perforated Mulan Leather",
  "143": "Gray Perforated Mulan Leather",
  "144": "Gray Leather w/ Sueded Microfiber Inserts",
  "145": "Gray Perforated Napa Leather",
  "146": "Gray Leather w/ Sueded Microfiber Inserts",
  "191": "Jet Black Perforated Mulan Leather",
  "192": "Jet Black Leather w/ Sueded Microfiber Inserts",
  "193": "Jet Black Perforated Mulan Leather",
  "194": "Jet Black Leather w/ Sueded Microfiber Inserts",
  "195": "Jet Black Perforated Napa Leather",
  "196": "Jet Black Leather w/ Sueded Microfiber Inserts",
  "198": "Jet Black Leather w/ Sueded Microfiber Inserts",
  "343": "Kalahari Perforated Mulan Leather",
  "344": "Kalahari Leather w/ Sueded Microfiber Inserts",
  "345": "Kalahari Perforated Napa Leather",
  "346": "Kalahari Leather w/ Sueded Microfiber Inserts",
  "701": "Adrenaline Red Perforated Mulan Leather",
  "703": "Adrenaline Red Perforated Mulan Leather",
  "704": "Adrenaline Red Leather w/ Sueded Microfiber Inserts",
  "705": "Adrenaline Red Perforated Napa Leather",
  "706": "Adrenaline Red Leather w/ Sueded Microfiber Inserts",
  "755": "Spice Red Perforated Mulan Leather",
  "000": "Jet Black w/ Orange Stitching Leather w/ Sueded Microfiber Inserts",
  // - C8
  "HTA": "Jet Black Mulan Leather w/ Perforated Inserts",
  "HTE": "Jet Black Napa Leather w/ Perforated Inserts",
  "HTJ": "Jet Black Performance Textile",
  "HTO": "Tension W/ Twilight Blue Dipped Napa Leather w/ Perforated Inserts",
  "HU1": "Sky Cool Gray Napa Leather w/ Perforated Inserts",
  "HU2": "Adrenaline Red Napa Leather w/ Perforated Inserts",
  "HU3": "Morello Red Dipped Napa Leather w/ Perforated Inserts",
  "HUE": "Natural Napa Leather w/ Perforated Inserts",
  "HUP": "Sky Cool Gray Mulan Leather w/ Perforated Inserts",
  "HUQ": "Adrernaline Red Mulan Leather w/ Perforated Inserts",
  "HUR": "Adrernaline Red Mulan Leather w/ Perforated Inserts",
  "HUL": "Adrernaline Red NAPA Leather w/ Perforated Inserts",
  "HU7": "Adrernaline Red NAPA Leather w/ Perforated SUEDED MICROFIBER Inserts",
  "HUA": "Adrernaline Red NAPA Leather w/ Perforated SUEDED MICROFIBER Inserts",
  "HZN": "Natural Dipped Napa Leather w/ Perforated Inserts",
  "HTM": "JET BLACK NAPA LEATHER W/ PERFORATED INSERTS",
  "HTP": "JET BLACK NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HTT": "JET BLACK NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HUN": "SKY COOL GRAY MULAN LEATHER W/ PERFORATED INSERTS",
  "HUK": "SKY COOL GRAY NAPA LEATHER W/ PERFORATED INSERTS",
  "HU6": "SKY COOL GRAY NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HU9": "SKY COOL GRAY NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HUV": "NATURAL MULAN LEATHER W/ PERFORATED INSERTS",
  "HTN": "NATURAL NAPA LEATHER W/ PERFORATED INSERTS",
  "HTQ": "NATURAL NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HTG": "NATURAL NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HUF": "NATURAL DIPPED NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HT7": "SKY COOL GRAY W/ STRIKE YELLOW NAPA LEATHER W/ PERFORATED INSERTS",
  "HFC": "SKY COOL GRAY W/ STRIKE YELLOW NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HNK": "ADDRENALINE RED DIPPED NAPA LEATHER W/ PERFORATED INSERTS",
  "HV1": "CERAMIC WHITE W/ RED STITCHING NAPA LEATHER W/ PERFORATED INSERTS",
  "HV2": "ARTEMIS NAPA LEATHER W/ PERFORATED INSERTS",
  "HUX": "HABANERO NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HUW": "HABANERO NAPA LEATHER W/ PERFORATED INSERTS",
  "HZB": "CUSTOM SKY COOL GRAY W/ JET BLACK ACCENTS NAPA LEATHER W/ PERFORATED INSERTS",
  "HVT": "CUSTOM SKY COOL GRAY W/ JET BLACK ACCENTS NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HVV": "CUSTOM JET BLACK W/ SKY COOL GRAY ACCENTS NAPA LEATHER W/ PERFORATED INSERTS",
  "HMO": "CUSTOM JET BLACK W/ SKY COOL GRAY ACCENTS NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HUU": "CUSTOM ADRENALINE RED W/ JET BLACK ACCENTS NAPA LEATHER W/ PERFORATED INSERTS",
  "HZP": "CUSTOM ADRENALINE RED W/ JET BLACK ACCENTS NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  "HU0": "CUSTOM JET BLACK W/ ADRENALINE RED ACCENTS NAPA LEATHER W/ PERFORATED INSERTS",
  "HXO": "CUSTOM JET BLACK W/ ADRENALINE RED ACCENTS NAPA LEATHER W/ PERFORATED SUEDED MICROFIBER INSERTS",
  // Camaro
  "H01": "Kalahari Leather",
  "H0W": "Jet Black Leather W/ Red accents",
  "H0Y": "Jet Black Leather",
  "H13": "Ceramic White Leather",
  "H16": "Adrenaline Red Leather",
  "H17": "Medium Ash Gray Leather",
  "H1T": "Jet Black Cloth",
  "H72": "Medium Ash Gray Cloth",
  // Cadillac
  "E2B": "Jet Black W/ Signet Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "E2D": "Jet Black W/ Adrenaline Red Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "E2G": "Jet Black W/ Sky Cool Gray Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "H0L": "Sangria W/ Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "H0M": "Cinnamon W/ Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "H1Y": "Jet Black W/ Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "H2G": "Jet Black W/ Jet Black Accents Inteluxe",
  // UNSURE "H2X": "JET BLACK LEATHER W/ CHEVRON PERFORATED INSERTS",
  "H2X": "Jet Black W/ Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "H66": "JET BLACK LEATHER",
  "HAV": "Maple Sugar W/ Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HBE": "Jet Black W/ Jet Black Accents Leather/Performance Cloth/Sueded Microfiber/Ineluxe and Sueded Front Seatbacks",
  "HBF": "Natural Tan W/ Jet Black Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "HEA": "Jet Black W/ Jet Black Accents Leather w/ Sueded Front Seatbacks",
  "HEB": "Sky Cool Gray W/ Jet Black Accents Leather w/ Sueded Front Seatbacks",
  "HGM": "Jet Black W/ Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HIK": "Sahara Beige W/ Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HIT": "Sahara Beige W/ Jet Black Accents Inteluxe",
  "HIZ": "SEMI-ANILINE LEATHER W/ CHEVRON PERFORATED INSERTS",
  "HJC": "Natural Tan W/ Jet Black Accents Full Semi-Aniline Leather w/ Mini-Perforated Inserts: Custom Quilting and Carbon Fiber Front Seatbacks",
  "HJD": "Sky Cool Gray W/ Jet Black Accents Full Semi-Aniline Leather w/ Mini-Perforated Inserts: Custom Quilting and Carbon Fiber Front Seatbacks",
  "HK1": "VERY LIGHT CASHMERE W/ MAPLE SUGAR ACCENTS SEMI-ANILINE LEATHER W/ CHEVRON PERFORATED INSERTS",
  "HMC": "Whisper Beige W/ Jet Black Accents Inteluxe",
  "HMQ": "SAHARA BEIGE W/ JET BLACK ACCENTS LEATHER W/ CHEVRON PERFORATED INSERTS",
  "HMR": "Jet Black W/ Jet Black Accents Full Semi-Aniline Leather w/ Mini-Perforated Inserts: Custom Quilting and Carbon Fiber Front Seatbacks",
  "HNC": "Whisper Beige W/ Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HND": "Whisper Beige W/ Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HTX": "DARK AUBURN W/ JET BLACK ACCENTS LEATHER W/ CHEVRON PERFORATED INSERTS",
  "HTZ": "SAHARA BEIGE W/ JET BLACK ACCENTS LEATHER",
  "HXR": "Jet Black W/ Jet Black Accents Inteluxe",
  "HZK": "Sedona Sauvage W/ Jet Black Accents Semi-Aniline Full Leather w/ Chevron Perforated Inserts",
  "HZQ": "Jet Black W/ Jet Black Accents Inteluxe",
  "EG1": "Sky Cool Gray W/ Santorini Blue Accents Leather W/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "E54": "Jet Black W/ Phantom Blue Accents Leather W/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "H9F": "Jet Black Evotex",
  "EMX": "Black Evotex",
  // Hummer EV
  "H9Z": "LUNAR HORIZON (JET BLACK/LIGHT GREY) Premium Leather-Alternative",
  "HAS": "LUNAR SHADOW (JET BLACK/TAUPE) Premium Leather-Alternative",
  "HBZ": "GRANITE DRIFT PREMIUM LEATHER-ALTERNATIVE",
  "HR5": "STEALTH ECLIPSE PREMIUM LEATHER-ALTERNATIVE",
  "EHM": "VELOCITY EMBER PREMIUM LEATHER-ALTERNATIVE",
  // Silverado EV
  "H7D": "Black Evotex",
  "EMW": "Black w/ Sky Cool Gray Evotex",
};

const seatCode = {
  // Camaro
  "A50": "Sport front buckets",
  "AQJ": "RECARO Performance front buckets",
  // Corvette
  "AE4": "Competition buckets",
  "AH2": "GT2 buckets",
  "AQ9": "GT1 buckets",
  // Cadillac
  "": "",
  // Silverado EV
  "AR9": "Front Bucket Seats",
};

const mmc = {
  // Camaro
  "1AG37": "1LT",
  "1AG67": "1LT",
  "1AH37": "2LT",
  "1AH67": "2LT",
  "1AJ37": "1SS",
  "1AJ67": "1SS",
  "1AK37": "2SS",
  "1AK67": "2SS",
  "1AL37": "1SE",
  "1AL67": "1SE",
  // Corvette SR C7
  "1YY07": "", // Coupe
  "1YY67": "", // Conv
  // Corvette GS C7
  "1YW07": "", // Coupe
  "1YW67": "", // Conv
  // Corvette SR Z51 C7
  "1YX07": "", // Coupe
  "1YX67": "", // Conv
  // Corvette Z06 C7
  "1YZ07": "", // Coupe
  "1YZ67": "", // Conv
  // Corvette ZR1 C7
  "1YV07": "", // Coupe
  "1YV67": "", // Conv
  // Corvette C8
  "1YC07": "", // Coupe
  "1YC67": "", // Conv
  // Corvette Z06 C8
  "1YH07": "", // Coupe
  "1YH67": "", // Conv
  // Corvette E-Ray C8
  "1YG07": "", // Coupe
  "1YG67": "", // Conv
  // Corvette ZR1 C8
  "1YR07": "", // Coupe
  "1YR67": "", // Conv
  // Cadillac
  "6DB69": "1SB", // CT4 LUXURY
  "6DB79": "1SB", // CT5 LUXURY
  "6DC69": "1SD", // CT4 PREMIUM LUXURY
  "6DC79": "1SD", // CT5 PREMIUM LUXURY
  "6DD69": "1SE", // CT4 SPORT
  "6DD79": "1SE", // CT5 SPORT
  "6DE69": "1SF", // CT4 V-SERIES
  "6DE79": "1SF", // CT5 V-SERIES
  "6DF69": "1SP", // CT4 V-SERIES BLACKWING
  "6DF79": "1SV", // CT5 V-SERIES BLACKWING
  "6KM69": "1SP", // CT6 PLATINUM
  "6KH69": "1SB", // CT6 LUXURY
  "6KJ69": "1SD", // CT6 PREMIUM LUXURY
  "6KN69": "1SV", // CT6 V-SERIES
  // Silverado EV
  "CT35843": "",
};

module.exports = {
  colorMap,
  intColor,
  seatCode,
  mmc
}
