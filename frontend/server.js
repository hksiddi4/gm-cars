const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const axios = require('axios');

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('views'));
app.set('view engine', 'ejs');

const baseURL = 'http://127.0.0.1:5000'

const rpoDescriptions = {
    "0ST":  "VAA/Component Rel",
    "19T":	"Convertible top color, Black",
    "1LT":  "Base Equipment Package",
    "1NF":  "VAA/Component",
    "1SZ":  "Option Package Discount",
    "2F5":	"Knee pads, Red",
    "2LT":  "Base Equipment Package",
    "2NF":  "VAA/Components",
    "2SS":  "Base Equipment Package",
    "2ST":  "VAA/Component",
    "3DL":	"Interior trim, carbon fiber instrument panel molding",
    "3F9":	"Seat belt color, Red",
    "3LT":  "Base Equipment Package",
    "4AA":  "Interior Trim",
    "56H":	"LPO, SS 20\" (50.8 cm) 5-spoke gloss Black wheels with Red stripe",
    "56K":	"LPO, SS 20\" (50.8 cm) 5-split spoke polished forged wheels with Black star center cap",
    "56M":	"LPO, SS 20\" (50.8 cm) 5-split spoke machined-face wheels",
    "56R":	"Wheels, 20\" x 8.5\" (50.8 cm x 21.6 cm) front and 20\" x 9.5\" (50.8 cm x 24.1 cm) rear 5-split spoke premium Gray-painted machined-face aluminum",
    "56S":	"Wheels, 20\" x 8.5\" (50.8 cm x 21.6 cm) front and 20\" x 9.5\" (50.8 cm x 24.1 cm) rear bright 5-spoke Silver-painted aluminum",
    "56V":	"Wheels, 20\" x 8.5\" (50.8 cm x 21.6 cm) front and 20\" x 9.5\" (50.8 cm x 24.1 cm) rear 5-spoke Carbon Flash painted aluminum",
    "56W":	"Wheels, 20\" x 8.5\" (50.8 cm x 21.6 cm) front and 20\" x 9.5\" (50.8 cm x 24.1 cm) rear 5-spilt spoke bright Silver-painted aluminum",
    "56Y":	"Wheels, 20\" x 8.5\" (50.8 cm x 21.6 cm) front and 20\" x 9.5\" (50.8 cm x 24.1 cm) rear blade design aluminum",
    "56Z":	"Wheels, 20\" x 8.5\" (50.8 cm x 21.6 cm) front and 20\" x 9.5\" (50.8 cm x 24.1 cm) rear 5-split spoke Black forged aluminum",
    "57S":	"LPO, SS 20\" (50.8 cm) 5-split spoke Satin Black wheels",
    "57V":	"Wheels, 20\" x 8.5\" (50.8 cm x 21.6 cm) front and 20\" x 9.5\" (50.8 cm x 24.1 cm) rear Caliente",
    "57W":	"Wheels, 20\" x 8.5\" (50.8 cm x 21.6 cm) front and 20\" x 9.5\" (50.8 cm x 24.1 cm) rear 5-split spoke polished forged aluminum with Black star center cap",
    "58E":	"Wheels, 20\" x 8.5\" (50.8 cm x 21.6 cm) front and 20\" x 9.5\" (50.8 cm x 24.1 cm) rear Black-painted aluminum with Red accents",
    "5A7":  "Spare Wheel Deletion GM Accessory",
    "5AA":  "Spare Wheel-None",
    "5JW":	"LPO, 20\" (50.8 cm) 5-split spoke polished forged wheels with Black star center cap",
    "5JX":	"LPO, LT 20\" (50.8 cm) 5-split spoke Satin Black wheels",
    "5K2":	"LPO, Decklid blackout decal",
    "5K9":	"Wheels, 20\" (50.8 cm) Caliente",
    "5KP":	"LPO, Illuminated sill plates",
    "5LQ":	"LPO, 6 Piston Front Brake Kit",
    "5V5":	"LPO, Body-color high-wing spoiler",
    "5V6":	"LPO, Black Interior Appearance Package",
    "5VF":	"LPO, Carbon fiber exhaust tip",
    "5VM":	"LPO, Ground Effects Package",
    "5WF":	"LPO, Battery Protection Package",
    "5YN":	"LPO, Carbon Fiber-look shift knob (auto) or Carbon Fiber-look shift knob medallion (manual)",
    "5ZB":	"LPO, Camaro logo wheel center caps",
    "5ZD":	"LPO, Wheel center caps",
    "5ZU":	"LPO, Body-color blade spoiler",
    "5ZV":	"LPO, Satin Black blade spoiler",
    "5ZW":	"LPO, Satin Black wing spoiler",
    "5ZZ":	"LPO, Carbon Flash Metallic blade spoiler",
    "62F":	"LPO, Premium carpeted cargo mat with Camaro logo",
    "62O":	"LPO, Clear CHMSL (Center High Mount Stop Lamp)",
    "6X1":  "Component",
    "6ZQ":	"LPO, ZL1 1LE SPEC visible carbon fiber spoiler",
    "7X1":  "Component",
    "8GW":  "Component RR LH",
    "9GW":  "Component RR RH",
    "9L3":  "Spare Tire - None",
    "A1X":	"1LE Track Performance Package",
    "A1Y":	"SS 1LE Track Performance Package",
    "A1Z":	"ZL1 1LE Extreme Track Performance Package",
    "A45":	"Memory Package",
    "A50":	"Seats, front Sport bucket",
    "A62":	"Seat, rear fixed",
    "A9B":	"Satin Black Appearance Package",
    "AAQ":	"Seat adjuster, front passenger",
    "AJ7":	"Airbags, frontal and side",
    "AJ9":	"Airbags, dual-stage frontal, knee, head and thorax side-impact, driver and front passenger",
    "AKQ":	"Seat adjuster, front passenger, 6-way power",
    "AL0":  "Airbag Sensing System, Front Passenger",
    "AM7":	"Seat, rear, folding",
    "AQJ":	"Seats, front bucket, RECARO performance",
    "ATH":	"Keyless Open and Start",
    "AT8":  "Latch System",
    "AV3":	"Seat adjuster, driver, 8-way power",
    "AXJ":  "Passenger Car",
    "AYG":	"Airbags, dual-stage frontal, thorax side-impact and knee, driver and front passenger, and head curtain side-impact",
    "B2E":	"Shock and Steel Special Edition",
    "B34":	"Floor mats, carpeted front",
    "B7G":	"Sill plates, illuminated",
    "B9M":	"Tail lamps, dark tint",
    "BCD":	"Performance copper-free brake system",
    "BO3":	"White Pearl Rally Stripes",
    "BO4":	"Black Metallic Rally Stripes",
    "BRD":	"Ceramic White Interior Package",
    "BRJ":	"Adrenaline Red Interior Package",
    "BTV":	"Remote vehicle starter system",
    "C2U":	"Silver Rally Stripes",
    "C3O":	"Black Rally Stripes",
    "C68":	"Air conditioning, single-zone automatic climate control",
    "C70":	"Lighting, interior spectrum",
    "CF5":	"Sunroof, power",
    "CFW":	"Hood insert, visible Carbon Fiber weave",
    "CG3":	"Emblem, Black Camaro fender badge",
    "CG6":	"Emblem, Black Camaro fender badge with Red outline",
    "CJ2":	"Air conditioning, dual-zone automatic climate control",
    "CM8":	"Convertible top, power-folding",
    "D31":	"Mirror, inside rearview manual day/night",
    "D52":	"Spoiler, rear",
    "D5S":	"Spoiler, rear, blade, Satin Black",
    "D5Z":	"Spoiler, rear, stanchion",
    "D80":	"Spoiler, decklid-mounted lip spoiler",
    "D88":	"1LE Hash Mark Decal",
    "DD1":	"Mirrors, outside heated power-adjustable and driver-side auto-dimming, body-color",
    "DD8":	"Mirror, inside rearview auto-dimming",
    "DG7":	"Mirrors, outside power-adjustable, body-color",
    "DG7":	"Mirrors, outside power-adjustable, body-color",
    "DNS":  "Dealer Installed Indicator",
    "DRZ":	"Rear Camera Mirror",
    "DSM":	"Hood wrap, Satin Black",
    "DUU":	"Black Center Stripe",
    "DUV":	"Silver Center Stripe",
    "DVV":	"Black Metallic Center Stripe",
    "DW7":	"White Pearl Center Stripe",
    "DW8":	"Black Metallic Center Stripe",
    "EF7":  "Country Code, U.S.A.",
    "F55":	"Magnetic Ride Control",
    "FE2":	"Suspension, Sport",
    "FE3":	"Suspension, Performance",
    "FE4":	"Suspension, Performance",
    "FE9":	"Emissions, Federal requirements",
    "FEA":	"Suspension, Performance",
    "FJW":  "Vehicle Fuel Gasoline",
    "FTF":	"Front splitter",
    "FTJ":	"Front splitter",
    "G16":  "Crush",
    "G1M":  "Blue Velvet Metallic",
    "G7C":  "Red Hot",
    "G7D":  "Bright Yellow",
    "G7E":  "Garnet Red Metallic",
    "G7Q":  "Nightfall Gray Metallic",
    "G80":	"Differential, limited slip",
    "G96":	"Differential, electronic limited-slip",
    "G9K":  "Satin Steel Gray Metallic",
    "GAN":  "Silver Ice Metallic",
    "GAZ":  "Summit White",
    "GB8":  "Mosaic Black Metallic",
    "GBA":  "Black",
    "GCF":  "Vivid Orange Metallic",
    "GCP":  "Nitro Yellow Metallic",
    "GD1":  "Hyper Blue Metallic",
    "GGB":  "Arctic Blue Metallic",
    "GJ0":  "Rally Green Metallic",
    "GJI":  "Shadow Gray Metallic",
    "GJV":  "Riptide Blue Metallic",
    "GKK":  "Riverside Blue Metallic",
    "GKO":  "Shock",
    "GLK":  "Panther Black Metallic",
    "GMO":  "Rapid Blue",
    "GMV":  "Krpton Green",
    "GNT":  "Radiant Red Tintcoat",
    "GNW":  "Panther Black Matte",
    "GSK":  "Wild Cherry Tintcoat",
    "GT4":	"Rear axle, 3.73 ratio",
    "GW6":	"Rear axle, 3.27 ratio",
    "GXD":  "Sharkskin Metallic",
    "H0Y":  "Jet Black Leather",
    "H1T":  "Jet Black Cloth",
    "HRD":	"Rear axle, 2.85 ratio",
    "HRE":	"Rear axle, 2.77 ratio",
    "IOR":	"Audio system, Chevrolet Infotainment 3 system, 7\" diagonal color touchscreen",
    "IOS":	"Audio system, Chevrolet Infotainment 3 Plus system, 8\" diagonal HD color touchscreen",
    "IOT":	"Audio system, Chevrolet Infotainment 3 Premium system with connected Navigation, 8\" diagonal HD color touchscreen",
    "J22":  " ",
    "J55":	"Brakes, Brembo 4-piston front, performance, 4-wheel antilock, 4-wheel disc",
    "J6E":	"Calipers, Yellow",
    "J6F":	"Calipers, Red",
    "J6G":	"Brakes, Brembo 4-piston front and rear, performance, 4-wheel antilock, 4-wheel disc",
    "J6H":	"Brakes, Brembo 6-piston front and 4-piston rear, performance",
    "J6L":	"Calipers, Orange",
    "J6M":	"Brakes, Brembo Red, 6-piston front monobloc calipers, 4-piston rear calipers, 2-piece rotors, performance",
    "J71":  "eBrake - Motor on Caliper",
    "J77":  "Brake, Electronic Parking",
    "JF5":	"Pedals, sport alloy",
    "JL9":	"Brakes, 4-wheel antilock, 4-wheel disc",
    "K05":	"Engine block heater",
    "K4C":	"Wireless Charging",
    "KA1":	"Seats, heated driver and front passenger",
    "KB7":	"Paddle-shift manual controls",
    "KC4":	"Cooling, external engine oil cooler",
    "KD1":	"Cooler, transmission oil",
    "KNR":	"Cooler, rear differential",
    "KQV":	"Seats, ventilated driver and front passenger",
    "KRV":  "Refrigerant",
    "KS9":	"Shift knob, sueded microfiber-wrapped",
    "KTI":	"Tire inflation kit",
    "LAL":  "Lansing Plant Grand River",
    "LGX":	"Engine, 3.6L V6, DI, VVT",
    "LT1":	"Engine, 6.2L (376 ci) V8 DI",
    "LT4":	"Engine, 6.2L supercharged V8",
    "LTG":	"Engine, 2.0L Turbo, 4-cylinder, SIDI, VVT",
    "M97":  "Brake/Trans Shift Interlock",
    "MAH":  "Marketing Area North America",
    "MCR":  "Receptable Memory Card",
    "MH3":  "Transmission, 6-speed manual - TR-6060",
    "MI2":  "Auto 10 Spd, Transmission",
    "MI3":  "Transmission, 6-speed manual - TR-3160",
    "MJK":  "Transmission, 6-speed manual - TR-6060",
    "MM6":  "Transmission, 6-speed manual - TR-6060",
    "MN6":	"Transmission, 6-speed manual",
    "MX0":	"Transmission, 10-speed automatic",
    "MX0":	"Transmission, 8-speed automatic",
    "N10":	"Exhaust, dual-outlet stainless-steel",
    "N26":	"Steering wheel, 3-spoke, sueded microfiber-wrapped, flat-bottom",
    "NB8":	"Emissions override, California",
    "NB9":	"Emissions override, state-specific",
    "NC7":	"Emissions override, Federal",
    "NE1":	"Emissions, Connecticut, Delaware, Maine, Maryland, Massachusetts, New Jersey, New York, Oregon, Pennsylvania, Rhode Island, Vermont and Washington state requirements",
    "NE8":  "Emissions",
    "NKC":  "Noise Control System",
    "NKE":  "Noise Control - Electronic Sound Enhancer",
    "NP5":	"Steering wheel, leather-wrapped",
    "NPP":	"Exhaust, dual-mode",
    "NTB":  "Emission System Federal",
    "NV9":	"Steering, power",
    "P0G":	"GM Commercial Link - 1 year of Service",
    "P0H":	"GM Commercial Link - 2 years of Service",
    "P0I":	"GM Commercial Link - 3 years of Service",
    "P0J":	"OnStar Additional 21 months of OnStar Fleet Safety and Security",
    "P0K":	"OnStar Additional 33 months of OnStar Fleet Safety and Security",
    "P0L":	"OnStar Additional 45 months of OnStar Fleet Safety and Security",
    "P0M":	"OnStar Additional 21 months of OnStar Fleet Driver Remote Access",
    "P0N":	"OnStar Additional 33 months of OnStar Fleet Driver Remote Access",
    "P0O":	"OnStar Additional 45 months of OnStar Fleet Driver Remote Access",
    "P0P":	"OnStar Additional 57 months of OnStar Fleet Driver Remote Access",
    "P0Q":	"OnStar Additional 57 months of OnStar Fleet Safety and Security",
    "P0R":	"OnStar Additional 9 months of OnStar Fleet Driver Remote Access",
    "P0U":	"OnStar Additional 9 months of OnStar Fleet Safety and Security",
    "P0V":	"OnStar Vehicle Insights - 1 year of Service",
    "P0W":	"OnStar Vehicle Insights - 2 years of Service",
    "P0X":	"OnStar Vehicle Insights - 3 years of Service",
    "P0Y":	"OnStar Vehicle Insights - 4 years of Service",
    "P0Z":	"OnStar Vehicle Insights - 5 years of Service",
    "P1R":	"OnStar Additional 9 months of OnStar Fleet Assurance",
    "P1S":	"OnStar Additional 21 months of OnStar Fleet Assurance",
    "P1T":	"OnStar Additional 33 months of OnStar Fleet Assurance",
    "P1U":	"OnStar Additional 45 months of OnStar Fleet Assurance",
    "P3H":	"Bowties, Black, front and rear",
    "PCH":	"LPO, Performance Enthusiast Package with Gray accents",
    "PCI":	"LPO, Performance Enthusiast Package with Red accents",
    "PCJ":	"LPO, Dark Tint Rear Lighting Package",
    "PCK":	"LPO, Black Accent Exterior Package",
    "PCL":	"LPO, Black Wheel Lug Nuts and Locks Package",
    "PCN":	"LPO, Winter/Summer Floor Mats Package",
    "PCR":	"LPO, Satin Black Front Splitter/Side Rockers Package",
    "PCU":	"LPO, 4-Corner Brembo brake upgrade system in Red",
    "PCV":	"LPO, RS/SS Interior Package",
    "PCW":	"LPO, Camaro Logo Premium Carpeted Mats Package",
    "PCX":	"LPO, Camaro Logo Package",
    "PCY":	"LPO, Red Accent Exterior Package",
    "PDB":	"LPO, Winter Protection Package",
    "PDL":	"Design Package 1",
    "PDN":	"Design Package 2",
    "PDP":	"Design Package 3",
    "PDV":	"LPO, Camaro Insignia Package",
    "PDX":	"LPO, ZL1 Protection Package",
    "PDY":	"LPO, Body-Color Spoiler with Wicker Package",
    "PKJ":	"Wheels, 19\" x 11\" (48.3 cm x 27.9 cm) front and 19\" x 12\" (48.3 cm x 30.48 cm) rear low gloss Black-painted forged aluminum",
    "PPW":	"Wireless Apple CarPlay/Wireless Android Auto",
    "PR6":	"SiriusXM, Additional 9 months of the SXM Platinum Plan",
    "PR7":	"SiriusXM, Additional 21 months of the SXM Platinum Plan",
    "PR8":	"SiriusXM, Additional 33 months of the SXM Platinum Plan",
    "PRF":	"3 Years of OnStar Remote Access",
    "Q7F":	"Wheels, 20\" (50.8 cm) blade design aluminum",
    "Q7G":	"Wheels, 20\" (50.8 cm) 5-split spoke Black forged aluminum",
    "R0F":	"Tires, 245/40ZR20 front and 275/35ZR20 rear, blackwall, summer-only",
    "R0G":	"Tires, 285/30R20 front and 305/30R20 rear, blackwall, summer-only",
    "R0H":	"Tires, 245/50R18, blackwall, all-season",
    "R29":	"Tires, 245/40R20, blackwall, all-season",
    "R6J":  "Ship Thru Code Acknowledgement",
    "R6O":	"Tires, 305/30R19 front and 325/30R19 rear, blackwall, summer-only",
    "R7E":  "ID-License Plate Bracket Charge",
    "R7Z":	"OnStar Additional 57 months of OnStar Fleet Assurance",
    "R88":	"LPO, Front illuminated and rear non-illuminated bowtie emblems in Black",
    "R8J":  "LGR-ID Camaro Coupe Models",
    "R8S":	"OnStar In-Vehicle Coaching - 1 Year of Service",
    "R8V":	"Not Equipped with Hood Insulator, see dealer for details.",
    "R9L":	"Deleted 3 Years of OnStar Remote Access",
    "R9N":  "VOMS Processing Option",
    "R9Y":	"Fleet Free Maintenance Credit",
    "REG":	"Wheels, 18\" (45.7 cm) Silver-painted aluminum",
    "RFR":	"OnStar In-Vehicle Coaching - 1 year of Service",
    "RFS":	"OnStar In-Vehicle Coaching - 2 Years of Service",
    "RFT":	"OnStar In-Vehicle Coaching - 3 Years of Service",
    "RFU":	"OnStar In-Vehicle Coaching - 4 Years of Service",
    "RFY":	"OnStar In-Vehicle Coaching - 5 Years of Service",
    "RIK":	"LPO, Black front and rear bowtie emblems",
    "RIN":	"LPO, Camaro logo fender badge",
    "RMH":	"LPO, Front splitter, Carbon Flash Metallic",
    "RNX":	"LPO, Outdoor vehicle cover",
    "RO1":	"LPO, Black lower grille with Silver-painted inserts",
    "RO2":	"LPO, Black lower grille with Gloss Black inserts",
    "RQ9":	"Wheels, 20\" (50.8 cm) 5-split spoke premium Gray-painted, machined-face aluminum",
    "RQA":	"Wheels, 20\" (50.8 cm) Silver-painted aluminum",
    "RSK":	"Wheels, 20\" x 10\" (50.8 cm x 25.4 cm) front and 20\" x 11\" (50.8 cm x 27.9 cm) rear Satin Graphite forged aluminum",
    "RTH":	"Wheels, 20\" (50.8 cm) 5-spoke Carbon Flash painted aluminum",
    "RTJ":	"Wheels, 20\" (50.8 cm) 5-spilt spoke bright Silver-painted aluminum",
    "RTQ":	"Wheels, 20\" x 10\" (50.8 cm x 25.4 cm) front and 20\" x 11\" (50.8 cm x 27.9 cm) rear Dark Graphite premium paint, forged aluminum",
    "RVK":	"LPO, Performance air intake",
    "RWH":	"LPO, Indoor vehicle cover",
    "RWJ":	"LPO, Outdoor vehicle cover",
    "RX0":	"LPO, 4 Piston Brembo rear calipers in Red",
    "RXH":	"LPO, Silver RS wheel center caps",
    "RXJ":	"LPO, Silver SS wheel center caps",
    "RY2":	"LPO, Black Metallic Hash Mark Stripes",
    "RZ3":	"LPO, Front splitter",
    "RZB":	"LPO, Black lower grille with Red Hot inserts",
    "S0O":	"LPO, Illuminated footwells",
    "S0U":	"LPO, Black sueded knee pads",
    "S0V":	"LPO, White knee pads",
    "S54":	"LPO, Navigation upgrade kit",
    "SA7":	"LPO, Suede shift knob and boot kit",
    "SB2":	"LPO, Carbon Flash Metallic wing spoiler",
    "SB3":	"LPO, ZL1 SPEC rear spoiler, body-color",
    "SB7":	"LPO, Red Spider Stripes",
    "SB9":	"LPO, Satin Black Spider Stripes",
    "SBF":  "Safety Belts",
    "SC1":	"LPO, Sway bar suspension upgrade system",
    "SCG":	"LPO, 6.2L Strut tower brace in Black",
    "SCJ":	"LPO, Suspension Handling Package, 1LE Track Pack - V8",
    "SCY":	"LPO, Dark finish tail lamps",
    "SF8":	"LPO, Silver Body-Side Spear Stripes",
    "SF9":	"LPO, Blue Hash Mark Stripes",
    "SFA":	"LPO, Red Stinger Stripe",
    "SFC":	"LPO, White Pearl Hash Mark Stripes",
    "SFE":	"LPO, Wheel locks",
    "SFZ":	"LPO, Camaro fender badge, Black",
    "SG3":	"LPO, Lowering suspension upgrade system",
    "SGE":	"Wheels, 18\" (45.7 cm) 5-split spoke Silver-painted aluminum",
    "SH1":	"LPO, Embroidered center console lid with Camaro badge",
    "SH2":	"LPO, Embroidered center console lid",
    "SHL":	"LPO, 20\" (50.8 cm) 5-spoke gloss Black wheels with Red outline stripe",
    "SHQ":	"LPO, Silver Hash Mark Stripes",
    "SHS":	"LPO, Satin Black Hood Stripe with Silver Ice Metallic Hash Mark",
    "SHT":	"Spoiler stripe",
    "SHU":	"LPO, Satin Black Hood Stripe with Red Hot Hash Mark",
    "SIA":	"LPO, Wicker bill",
    "SIB":	"LPO, Interior spectrum lighting, Dark Night",
    "SIC":	"LPO, Interior spectrum lighting, Red Day, Satin Red and Gloss Red pattern finish",
    "SJ8":	"LPO, Interior spectrum lighting, Structura",
    "SKW":	"LPO, 20\" (50.8 cm) 5-split spoke machined-face wheels",
    "SL1":	"LPO, Indoor vehicle cover",
    "SL2":	"LPO, Front splitter",
    "SLN":	"LPO, Strut tower brace",
    "SLM":  "Stock Orders",
    "SNB":	"LPO, Silver Spider Stripes",
    "SNC":	"LPO, White Pearl Spider Stripes",
    "SNE":	"LPO, Silver Stinger Stripe",
    "SNG":	"LPO, Red Hash Mark Stripes",
    "SNH":	"LPO, White Pearl Body-Side Spear Stripes",
    "SNJ":	"LPO, Satin Black Stinger Stripe",
    "SNM":	"LPO, White Pearl Stinger Stripe",
    "SNP":	"LPO, Red Body-Side Spear Stripes",
    "SNQ":	"LPO, Gray Body-Side Spear Stripes",
    "SNS":	"LPO, Blue Body-Side Spear Stripes",
    "SPY":	"LPO, Black lug nuts",
    "SPZ":	"LPO, Black wheel locks",
    "SRI":	"Wheels, 20\" (50.8 cm) Black-painted aluminum with Red accents",
    "STI":	"LPO, Satin Black rocker moldings",
    "T3S":  "Daytime Running Lamps",
    "T42":	"Spoiler, rear, visible weave carbon fiber",
    "T4L":  "Headlamps LED",
    "T61":  "Lamp System Daytime Running",
    "TD2":  "Ship Thru - Ground Effects",
    "TDM":	"Teen Driver",
    "U2K":	"SiriusXM",
    "U77":	"Antenna, integral rear window",
    "U80":  "Compass Display",
    "UB3":	"Antenna, AM/FM",
    "UD7":	"Rear Park Assist",
    "UDD":	"Driver Information Center, color display",
    "UE1":	"OnStar and Chevrolet connected services capable",
    "UEU":	"Forward Collision Alert",
    "UFG":	"Rear Cross Traffic Alert",
    "UHS":	"Driver Information Center",
    "UJM":  "Tire Pressure Monitor System",
    "UKC":	"Lane Change Alert",
    "UMN":	"Speedometer, miles/kilometers",
    "UPG":	"Bluetooth for phone",
    "UQ3":	"Audio system feature, 6-speaker system",
    "UQA":	"Audio system feature, Bose premium 9-speaker system",
    "UQA":	"Audio system feature, Bose premium 7-speaker system",
    "UQT":	"Performance data and video recorder",
    "UST":  "Audio system feature, USB port",
    "UV6":	"Head-Up Display",
    "UVB":	"HD Rear Vision Camera",
    "UVD":	"Steering wheel, heated",
    "V03":	"Cooling system, extra capacity",
    "V18":	"Cooler, engine coolant",
    "V8D":  "Vehicle Statement US",
    "VAV":	"LPO, All-weather floor mats",
    "VDN":	"LPO, Indoor vehicle cover",
    "VEB":	"LPO, Sport pedals kit",
    "VGS":	"LPO, Outdoor vehicle cover, Gray, ZL1 logo",
    "VK3":	"License plate bracket, front",
    "VLI":	"LPO, All-weather cargo mat",
    "VLN":	"LPO, Windscreen",
    "VPO":	"LPO, Gray Hash Mark Stripes",
    "VPW":	"LPO, Black Metallic Body-Side Spear Stripes",
    "VQG":	"LPO, Weather Protection Package",
    "VQL":	"LPO, Fuel filler door in Black with visible carbon fiber insert",
    "VRG":  "VAA/Component Rel Cockpit",
    "VRH":  "VAA/Component Rel Steering Column",
    "VRJ":  "VAA/Component Rel Powertrain Dress",
    "VRK":  "VAA/Component Rel Roof Trim",
    "VRL":  "VAA/Component Rel Front Horizontal Suspension",
    "VRG":  "VAA/Component Rel Cockpit",
    "VRM":  "VAA/Component Rel Front Vertical Suspension",
    "VRN":  "VAA/Component Rel Rear Suspension",
    "VRR":  "Component",
    "VRU":	"LPO, Outdoor vehicle cover, Gray",
    "VRV":	"LPO, Body-color painted splash guards",
    "VT7":  "Owners Manual",
    "VTA":	"LPO, Black exhaust tip",
    "VTD":	"LPO, Ground effects, Carbon Flash Metallic",
    "VTF":	"LPO, Embroidered center console lid",
    "VTG":	"LPO, White Interior Trim Kit",
    "VTU":	"LPO, Fuel filler door in Black with Gloss Black insert",
    "VUP":	"Redline Edition graphics",
    "VV4":	"Wi-Fi Hotspot capable",
    "VW9":	"LPO, Black SS wheel center caps",
    "VWD":	"LPO, Gloss Black wheel center caps with Silver bowtie",
    "VY7":	"Shift knob, leather-wrapped",
    "VYV":	"LPO, Short",
    "VYW":	"LPO, Floor mats, premium carpeted",
    "VYX":	"LPO, Painted engine cover",
    "W0D":	"LPO, Fuel filler door in Black with Red Hot insert",
    "W0E":	"LPO, Fuel filler door in Black with Silver Ice Metallic insert",
    "W1V":	"LPO, Floor mats, premium carpeted",
    "W2D":	"LPO, Cargo net",
    "WBL":	"Redline Edition",
    "WGK":	"LPO, Red Interior Trim Kit",
    "WGL":	"LPO, Kalahari knee pads",
    "WGT":	"LPO, Black Interior Trim Kit",
    "WHA":	"LPO, Red knee pads",
    "WL2":	"LPO, Floor mats, premium carpeted with 1LE performance logo",
    "WL3":	"LPO, Premium carpeted floor mats",
    "WMW":  "VIN Model Year 2022",
    "WR1":	"Wheels, 20\" (50.8 cm) 5-split spoke polished forged aluminum with Black star center cap",
    "WRS":	"RS Package",
    "X56":	"Garage 56 Edition",
    "XL8":  "Frequency Rating",
    "XLC":	"Launch control, custom",
    "Y3W":	"Technology Package",
    "Y4Q":	"Heavy-Duty Cooling and Brake Package",
    "YF5":	"Emissions, California state requirements",
    "YM8":  "Identification - LPO",
    "Z4B":	"Camaro Collector Edition",
    "ZN2":	"Convenience and Lighting Package"
};

function numberWithCommas(x) {
    if (x === null) return null;
    if (typeof x === 'string' && !isNaN(x)) {
        x = parseFloat(x); // Convert string to number
    }
    if (typeof x !== 'number') return x; // Return the value unchanged if it's not a number
    if (Number.isInteger(x)) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    } else {
        return x.toFixed(2).replace(/\.00$/, "").toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
}

app.get('/', function(req, res) {
    res.render('pages/index', { req: req });
});

app.get('/all', function(req, res) {
    const page = req.query.page || 1;  // Get the page number from the query parameter
    axios.get(`${baseURL}/all?page=${page}`)
    .then((response)=>{
        var all_data = response.data;

        all_data.forEach(function(data) {
            data.MSRP = numberWithCommas(data.MSRP);
        });

        res.render('pages/all', {
            req: req,
            all_data: all_data
        });
    })
});

app.get('/msrp', function(req, res) {
    axios.get(`${baseURL}/msrp`)
    .then((response)=>{
        var msrp_data = response.data;

        msrp_data.forEach(function(data) {
            data.MSRP = numberWithCommas(data.MSRP);
        });

        res.render('pages/msrp', {
            msrp_data: msrp_data
        });
    })
});

app.get('/panther350', function(req, res) {
    axios.get(`${baseURL}/panther350`)
    .then((response)=>{
        var ce_data = response.data;

        ce_data.forEach(function(data) {
            data.MSRP = numberWithCommas(data.MSRP);
            data.MARKUP = numberWithCommas(data.MARKUP);
        });

        res.render('pages/panther350', {
            ce_data: ce_data
        });
    })
});

app.get('/search', function(req, res) {
    var vin = req.query.vin; // Retrieve the VIN from the request query parameters
    axios.get(`${baseURL}/search?vin=${vin}`)
    .then((response)=>{
        var vin_data = response.data;

        vin_data.forEach(function(data) {
            data.MSRP = numberWithCommas(data.MSRP);
        });

        res.render('pages/search', {
            req: req,
            vin_data: vin_data,
            rpoDescriptions: rpoDescriptions
        });
    })
});

app.get('/test', function(req, res) {
    axios.get(`${baseURL}/test`)
    .then((response)=>{
        var vin_data = response.data;

        vin_data.forEach(function(data) {
            data.MSRP = numberWithCommas(data.MSRP);
        });

        res.render('pages/test', {
            req: req,
            vin_data: vin_data,
            rpoDescriptions: rpoDescriptions
        });
    })
});

const port = 8080;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
