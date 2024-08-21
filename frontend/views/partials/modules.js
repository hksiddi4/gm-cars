const colorMap = {
  "ARGENT SILVER METALLIC": "GXD",
  "BLACK": "GBA",
  "BLACK DIAMOND TRICOAT": "GLK",
  "BLACK RAVEN": "GBA",
  "BLAZE METALLIC": "GCF",
  "COASTAL BLUE METALLIC": "GJV",
  "CRUSH": "G16",
  "CRYSTAL WHITE TRICOAT": "G1W",
  "CYBER YELLOW METALLIC": "GCP",
  "DARK EMERALD FROST": "G7W",
  "DARK MOON METALLIC": "GLU",
  "ELECTRIC BLUE": "GMO",
  "EVERGREEN METALLIC": "GJ0",
  "GARNET METALLIC": "GLR",
  "GARNET RED TINTCOAT": "G7E",
  "INFRARED TINTCOAT": "GSK",
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
  "SHADOW GRAY METALLIC": "GJI",
  "SHADOW METALLIC": "GJI",
  "SHARKSKIN METALLIC": "GXD",
  "SHOCK": "GKO",
  "SUMMIT WHITE": "GAZ",
  "VELOCITY RED": "G7C",
  "VIVID ORANGE METALLIC": "GCF",
  "WAVE METALLIC": "GKK",
  "WILD CHERRY TINTCOAT": "GSK"
};

const intColor = {
  "Jet Black with Signet Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks": "E2B",
  "Jet Black with Adrenaline Red Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks": "E2D",
  "Jet Black with Sky Cool Gray Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks": "E2G",
  "Kalahari Leather": "H01",
  "Sangria with Jet Black Accents Leather w/ Mini-Perforated Inserts": "H0L",
  "Cinnamon with Jet Black Accents Leather w/ Mini-Perforated Inserts": "H0M",
  "Jet Black Leather with Red accents": "H0W",
  "Jet Black Leather": "H0Y",
  "Ceramic White Leather": "H13",
  "Adrenaline Red Leather": "H16",
  "Medium Ash Gray Leather": "H17",
  "Jet Black Cloth": "H1T",
  "Jet Black with Jet Black Accents Leather w/ Mini-Perforated Inserts": "H1Y",
  "Jet Black with Jet Black Accents Inteluxe": "H2G",
  "Jet Black with Jet Black Accents Leather w/ Mini-Perforated Inserts": "H2X",
  "Medium Ash Gray Cloth": "H72",
  "Maple Sugar with Jet Black Accents Leather w/ Mini-Perforated Inserts": "HAV",
  "Jet Black with Jet Black Accents Leather/Performance Cloth/Sueded Microfiber/Ineluxe and Sueded Front Seatbacks": "HBE",
  "Natural Tan with Jet Black Accents Leather w/ Mini-Perforated Custom Quilted Inserts and Sueded Front Seatbacks": "HBF",
  "Jet Black with Jet Black Accents Leather w/ Sueded Front Seatbacks": "HEA",
  "Sky Cool Gray with Jet Black Accents Leather w/ Sueded Front Seatbacks": "HEB",
  "Jet Black with Jet Black Accents Leather w/ Mini-Perforated Inserts": "HGM",
  "Sahara Beige with Jet Black Accents Leather w/ Mini-Perforated Inserts": "HIK",
  "Sahara Beige with Jet Black Accents Inteluxe": "HIT",
  "Natural Tan with Jet Black Accents Full Semi-Aniline Leather w/ Mini-Perforated Inserts: Custom Quilting and Carbon Fiber Front Seatbacks": "HJC",
  "Sky Cool Gray with Jet Black Accents Full Semi-Aniline Leather w/ Mini-Perforated Inserts: Custom Quilting and Carbon Fiber Front Seatbacks": "HJD",
  "Whisper Beige with Jet Black Accents Inteluxe": "HMC",
  "Jet Black with Jet Black Accents Full Semi-Aniline Leather w/ Mini-Perforated Inserts: Custom Quilting and Carbon Fiber Front Seatbacks": "HMR",
  "Whisper Beige with Jet Black Accents Leather w/ Mini-Perforated Inserts": "HNC",
  "Whisper Beige with Jet Black Accents Leather w/ Mini-Perforated Inserts": "HND",
  "Jet Black with Jet Black Accents Inteluxe": "HXR",
  "Sedona Sauvage with Jet Black Accents Semi-Aniline Full Leather w/ Chevron Perforated Inserts": "HZK",
  "Jet Black with Jet Black Accents Inteluxe": "HZQ"
}

const mmc = {
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
  mmc
}
