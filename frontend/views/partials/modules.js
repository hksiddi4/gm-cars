const colorMap = {
  "ACCELERATE YELLOW METALLIC": "GD0",
  "ARCTIC WHITE": "G8G",
  "ARGENT SILVER METALLIC": "GXD",
  "BLACK DIAMOND TRICOAT": "GLK",
  "BLACK RAVEN": "GBA",
  "BLACK": "GBA",
  "BLADE SILVER METALLIC": "GAN",
  "BLAZE METALLIC": "GCF",
  "CERAMIC MATRIX GRAY METALLIC": "G9F",
  "COASTAL BLUE METALLIC": "GJV",
  "CRUSH": "G16",
  "CRYSTAL WHITE TRICOAT": "G1W",
  "CYBER YELLOW METALLIC": "GCP",
  "DARK EMERALD FROST": "G7W",
  "DARK MOON METALLIC": "GLU",
  "ELECTRIC BLUE": "GMO",
  "ELKHART LAKE BLUE METALLIC": "GS7",
  "EVERGREEN METALLIC": "GJ0",
  "GARNET METALLIC": "GLR",
  "GARNET RED TINTCOAT": "G7E",
  "INFRARED TINTCOAT": "GSK",
  "LONG BEACH RED METALLIC": "G1E",
  "MAVERICK NOIR FROST": "GNW",
  "MERCURY SILVER METALLIC": "GKA",
  "MIDNIGHT SKY METALLIC": "GXE",
  "MIDNIGHT STEEL METALLIC": "GXU",
  "NITRO YELLOW METALLIC": "GCP",
  "PANTHER BLACK MATTE": "GNW",
  "PANTHER BLACK METALLIC": "GLK",
  "RADIANT RED TINTCOAT": "GNT",
  "RALLY GREEN METALLIC": "GJ0",
  "RAPID BLUE": "GMO",
  "RED HOT": "G7C",
  "RED OBSESSION TINTCOAT": "G7E",
  "RIFT METALLIC": "GRW",
  "RIPTIDE BLUE METALLIC": "GJV",
  "RIVERSIDE BLUE METALLIC": "GKK",
  "ROYAL SPICE METALLIC": "GLL",
  "SATIN STEEL GREY METALLIC": "G9K",
  "SATIN STEEL METALLIC": "G9K",
  "SEBRING ORANGE": "G26",
  "SHADOW GRAY METALLIC": "GJI",
  "SHADOW METALLIC": "GJI",
  "SHARKSKIN METALLIC": "GXD",
  "SHOCK": "GKO",
  "SUMMIT WHITE": "GAZ",
  "TORCH RED": "GKZ",
  "VELOCITY RED": "G7C",
  "VIVID ORANGE METALLIC": "GCF",
  "WAVE METALLIC": "GKK",
  "WILD CHERRY TINTCOAT": "GSK",
  "ZEUS BRONZE METALLIC": "GUI"
};

const intColor = {
  // Corvette
  "HTA": "Jet Black Mulan Leather w/ Perforated Inserts",
  "HTE": "Jet Black Napa Leather w/ Perforated Inserts",
  "HTJ": "Jet Black Performance Textile",
  "HTO": "Tension/Twilight Blue Dipped Napa Leather w/ Perforated Inserts",
  "HU1": "Sky Cool Gray Napa Leather w/ Perforated Inserts",
  "HU2": "Adrenaline Red Napa Leather w/ Perforated Inserts",
  "HU3": "Morello Red Dipped Napa Leather w/ Perforated Inserts",
  "HUE": "Natural Napa Leather w/ Perforated Inserts",
  "HUP": "Sky Cool Gray Mulan Leather w/ Perforated Inserts",
  "HUQ": "Adrernaline Red Mulan Leather w/ Perforated Inserts",
  "HZN": "Natural Dipped Napa Leather w/ Perforated Inserts",
  // Camaro
  "H01": "Kalahari Leather",
  "H0W": "Jet Black Leather with Red accents",
  "H0Y": "Jet Black Leather",
  "H13": "Ceramic White Leather",
  "H16": "Adrenaline Red Leather",
  "H17": "Medium Ash Gray Leather",
  "H1T": "Jet Black Cloth",
  "H72": "Medium Ash Gray Cloth",
  // Cadillac
  "E2B": "Jet Black with Signet Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "E2D": "Jet Black with Adrenaline Red Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "E2G": "Jet Black with Sky Cool Gray Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "H0L": "Sangria with Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "H0M": "Cinnamon with Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "H1Y": "Jet Black with Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "H2G": "Jet Black with Jet Black Accents Inteluxe",
  "H2X": "Jet Black with Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HAV": "Maple Sugar with Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HBE": "Jet Black with Jet Black Accents Leather/Performance Cloth/Sueded Microfiber/Ineluxe and Sueded Front Seatbacks",
  "HBF": "Natural Tan with Jet Black Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks",
  "HEA": "Jet Black with Jet Black Accents Leather w/ Sueded Front Seatbacks",
  "HEB": "Sky Cool Gray with Jet Black Accents Leather w/ Sueded Front Seatbacks",
  "HGM": "Jet Black with Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HIK": "Sahara Beige with Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HIT": "Sahara Beige with Jet Black Accents Inteluxe",
  "HJC": "Natural Tan with Jet Black Accents Full Semi-Aniline Leather w/ Mini-Perforated Inserts: Custom Quilting and Carbon Fiber Front Seatbacks",
  "HJD": "Sky Cool Gray with Jet Black Accents Full Semi-Aniline Leather w/ Mini-Perforated Inserts: Custom Quilting and Carbon Fiber Front Seatbacks",
  "HMC": "Whisper Beige with Jet Black Accents Inteluxe",
  "HMR": "Jet Black with Jet Black Accents Full Semi-Aniline Leather w/ Mini-Perforated Inserts: Custom Quilting and Carbon Fiber Front Seatbacks",
  "HNC": "Whisper Beige with Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HND": "Whisper Beige with Jet Black Accents Leather w/ Mini-Perforated Inserts",
  "HXR": "Jet Black with Jet Black Accents Inteluxe",
  "HZK": "Sedona Sauvage with Jet Black Accents Semi-Aniline Full Leather w/ Chevron Perforated Inserts",
  "HZQ": "Jet Black with Jet Black Accents Inteluxe"
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
  "": ""
};

const mmc = {
  // Camaro
  "1AG37": "1LT",
  "1AG37": "1LS",
  "1AG67": "1LT",
  "1AH37": "2LT",
  "1AH37": "3LT",
  "1AH67": "2LT",
  "1AH67": "3LT",
  "1AJ37": "LT1",
  "1AJ37": "1SS",
  "1AJ67": "LT1",
  "1AJ67": "1SS",
  "1AK37": "2SS",
  "1AK67": "2SS",
  "1AL37": "1SE",
  "1AL67": "1SE",
  // Corvette
  "1YC07": "", // Coupe
  "1YC67": "", // Conv
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
  "6DF79": "1SV" // CT5 V-SERIES BLACKWING
};

module.exports = {
  colorMap,
  intColor,
  seatCode,
  mmc
}
