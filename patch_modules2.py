import sys
import json

lines = """5AV	LPO, GM Energy PowerShift Charger, Residential bidirectional EV charger
5CH	LPO, GM PowerUp 2 (J1772) Charger, Residential EV charger
5WI	LPO, Utility Wall Latch Kit
9L3	Tire, spare, none
A2X	Seat adjuster
A45	Memory settings
A7K	Seat adjuster
AGG	Glass, laminated, front side, solar glazing
AHV	Power Hood
AKO	Glass, deep-tinted
AR9	Seats, front bucket
ARU	Window
AT8	LATCH system (Lower Anchors and Tethers for CHildren), for child restraints seats
ATH	Keyless Open
AU3	Door locks, power
AVI	Seat Belt Adjustable Guide Loops
AYH	Airbags
B30	Floor covering, color-keyed carpeting
BKG	Floor mats, front, carpeted
BKL	Floor mats, rear, carpeted
BTT	Alarm, remote panic
BTV	Remote vehicle starter system
BVE	Assist steps, Black
C49	Defogger, rear-window
C59	Air vents, rear
CE1	Wipers, front rain-sensing
CFF	Roof, panoramic fixed glass
CGN	Bed Liner, Spray-on
CJ2	Climate control, dual-zone automatic
CTB	Intersection Automatic Emergency Braking
CTT	Hitch Guidance
D53	Console, floor
D75	Door handles, body-color
DP6	Mirror caps
DRZ	Rear Camera Mirror
DX6	Mirrors
DXR	Mirrors, outside heated, power adjustable
E63	Pickup bed
EBI	Map pockets, driver and front passenger seatbacks
EMI	Black GMC badge
EN0	Engine, none
EN5	Tailgate, locking
EPH	Electronic Precision Shift
ESG	MultiPro Midgate
ETI	Battery Pack
ETN	Battery Pack
F45	Chassis, Continuous Damping Adaptive Ride Control 
F46	Chassis
F47	Suspension
FE9	Emissions, Federal requirements
GGC	Perimeter Grille Illumination 
HS1	Safety Alert Seat
ISA	Speed Limit Assist, automatic
JCF	Brake rotor, FNC
JL1	Trailer brake controller, integrated
JSV	Brakes, front and rear sliding caliper disc
K12	Air filter, pollutant
K2O	Power Station Pro
K7A	Wireless Phone Charging
KAM	Front Seats, heated front driver and passenger cushion and back with dual mode switches
KCB	Rear Seats, heated rear outboard passenger cushion 
KD4	Power outlet, front console, 12-volt
KI3	Steering wheel, heated
KI6	Power outlet, 120-volt
KPB	Power outlet, 110-volt, located in the eTrunk 
KRV	Air conditioning, refrigerant
KSG	Adaptive Cruise Control
KTI	Tire inflator kit
KU9	Seats, ventilated driver and front passenger
KV7	Power Station
KWP	Alternator, none
MF1	Transmission, none
N38	Steering column, power tilt and telescoping
N5G	Super Cruise Steering wheel, wrapped
NB8	Emissions override, California 
NB9	Emissions override, state-specific
NC7	Emissions override, Federal
NCH	Door locks, rear child security
NE1	Emissions, Colorado, Connecticut, Delaware, Maine, Maryland, Massachusetts, Minnesota, Nevada, New Jersey, New York, Oregon, Pennsylvania, Rhode Island, Vermont, Virginia and Washington state requirements
NF6	Emission system zero emission vehicle (ZEV)
NYS	Steering
P8N	Rear Drive Unit, rear
PCV	LPO, Interior Protection Package
PCW	LPO, Cargo Package
PCX	LPO, Bed Wall Organizer Package
PCY	LPO, Floor Liner and Hard Truck Bed Cover Package
PD7	Wheel, spare, none
PSC	Dual Level Charge Cord
PZ8	Hitch View
QK2	Tailgate, GMC MultiPro Tailgate
QMP	Tires, LT275/50R24, all-season blackwall
QT5	Tailgate, gate function manual with EZ Lift, includes power lock and release
R6P	3 Years SiriusXM
R9L	Deleted OnStar Basics (OnStar Fleet Basics for Fleet)
R9M	3 Years of Super Cruise and Digital Services by OnStar
R9V	Mobile Service Plus
R9W	Deleted Mobile Service Plus
R9Y	Mobile Service Plus
REE	Wheels, 24" X 9.0" aluminum
RIA	LPO, All-weather floor liner
RSI	LPO, Truck Bed Organizer, collapsible, (dealer-installed) 
RSR	Rear Seat Reminder
RVY	LPO, Bedside Utility Wall
RYC	LPO, All-Weather eTrunk Mat
RYZ	LPO, NACS DC Adapter
S4K	LPO, Flexible Cargo Organizer
S80	Front Drive Unit, front
T3U	Fog lamps
T3V	Lamps, cargo
T4L	Headlamps, LED
T8Z	Buckle to Drive
TDA	Teen Driver
THS	Trailering Assist Guidelines
TQ5	IntelliBeam
TRG	Trailer Camera Provisions
TSQ	Lamp Package, interior, deluxe
U2K	SiriusXM with 360L
U5G	5G vehicle connectivity
UBI	USB ports
UBJ	USB ports
UBK	USB port
UE1	OnStar services capable
UE4	Following Distance Indicator
UEN	Seat belt, front passenger presence detector
UET	Smart Trailer Integration Indicator
UEU	Forward Collision Alert
UF2	LED Cargo Area Lighting
UFB	Rear Cross Traffic Braking
UG1	Universal Home Remote
UGN	Enhanced Automatic Emergency Braking
UH5	Seat belt indicator, rear passengers
UJN	Tire Pressure Monitoring System
UK3	Steering wheel audio controls
UKK	Rear Pedestrian Alert
UKL	Super Cruise
UKT	Front Pedestrian and Bicyclist Braking 
UKW	Blind Zone Steering Assist with Trailering
ULM	Driver Attention Assist
UOW	Side Bicyclist Alert
UQA	Audio system feature, Bose premium 7-speaker system
URC	Drive Mode Control
URG	Driver Information Center
URR	Audio System
UTJ	Theft-deterrent system
UV2	HD Surround Vision
UV6	Head-Up Display
UVN	Bed View Camera
UVX	Traffic Sign Recognition
UVZ	Reverse Automatic Braking
VGC	Protector film
VK3	License plate kit, front
VMK	LPO, Cargo Management System Rails
VOZ	LPO, Hard Folding Truck Bed Cover by RealTruck Advantage
VPB	LPO, Soft rolling Truck Bed Cover
VSX	Trailering Information Label
VV4	Wi-Fi Hotspot capable
WD9	Seat, rear 60/40 split with center arm rest and cargo with MultiPro Midgate
WH9	LPO, eTrunk Vertical Cargo Area Divider
WLN	Windows
WMI	Active Aero Shutters, upper and lower
XRJ	Dual Motor 4WD
YF5	Emissions, California state requirements
ZL6	ProGrade Trailering System
5A7	Wheel, spare, none
A68	Seat, rear 60/40 folding bench
A7E	Seat adjuster, front passenger 4-way manual
A8H	Premium Package
AL9	Seat, driver 2-way power lumbar
AS2	Assisted Driving Package
AS3	Super Cruise Package
AVK	Seat adjuster, driver 4-way power lumbar
AVU	Seat adjuster, front passenger 4-way power
CWM	Technology Package
DD8	Mirror, inside rearview auto-dimming
EWX	Battery Pack
F89	Suspension, High Stance
FE2	Suspension, standard
K28	AC Charging, 11 kW
KV9	Inverter, 400 watt, with one 120 volt bed outlet
N37	Steering column, manual tilt and telescoping
PDM	AT4 Premium Package
PDN	LPO, Elevation Dark Package
PJ6	Transit Wheel, 22"l, 22"
PRB	3 Years OnStar One
Q8G	Wheels, 18" X 8.5" aluminum Machine Face Wheel with Gloss Black Painted Pockets
QMN	Tires, LT275/50R22, all-season blackwall 
QTZ	Tires, LT285/75R18E, all-terrain blackwall
QWJ	Tires, LT265/70R18, all-season blackwall
R8S	OnStar One Super Cruise Extension to 8 Years
RIK	LPO, Emblems
RRM	Wheels, 18" X 8.5" aluminum Machine Face Wheel with Low Gloss Painted Pockets
RWV	LPO, eTrunk sliding tray
RYH	LPO, GM NACS Level 2 Adapter, residential AC adapter for use on NACS Level 2 chargers
RYO	LPO, Roof sunshade
RYU	LPO, NACS DC Adapter
S1H	LPO, Off-Road Recovery Kit
S1O	LPO, Console-Mounted Safe
SAX	LPO, MultiPro Tailgate Audio System by Kicker
SES	LPO, 22" (55.9 cm) Black painted aluminum wheels, (dealer-installed)
SEU	LPO, 22" (55.9 cm) Gloss black wheels with machine face, (dealer-installed)
SFE	LPO, Wheel locks
SG8	Wheel, spare, 18" X 8.0" (45.7 cm x 20.3 cm), steel
SIY	Wheels, 22" X 9.0" (55.9 cm x 22.9 cm) aluminum Wheel with Ultrabright Machining, Painted Inserts, Painted Pockets, and Laser Etched Denali logo
SMI	Wheels, 22" X 9.0" (55.9 cm x 22.9 cm) aluminum Painted Deep Space Wheel with Gloss Black Painted Pockets and High Gloss Black Painted Inserts
SPY	LPO, Wheel lug nuts, Black
SPZ	LPO, Black lug nut and wheel lock kit
SWS	Ride Control Package
TGC	Headlamps
TGD	Headlamps
TGE	Headlamps
UD5	Front and Rear Park Assist
UKI	Blind Zone Steering Assist
UKM	Lane Keep Assist with Lane Departure Warning, enhanced
UKZ	Enhanced Automatic Parking Assist
UQF	Audio system feature, 6-speaker system
VBJ	LPO, Underseat storage
VBP	LPO, Power Distribution Box
VQK	LPO, Splash guards, molded
WH6	LPO, eTrunk Vertical Cargo Net, (dealer-installed)
WLM	Windows
YDH	Denali Reserve
YDM	Denali Premium
Z7X	Chassis, 2" Lift
ZBD	Tire, spare LT225/65R18, all-season blackwall 
ZM9	Comfort and Convenience Package
5JL	LPO, Front and Rear Performance Brake Kit
63G	LPO, GMC MultiPro tailgate Step Lights
65C	Label warning, California, Prop 65 compliant
JBV	Braking, regenerative
KC9	Power outlet
PEB	LPO, Level 2 and Fast Charging Adapter Package (Dealer Provided)
PEC	LPO, Charging Essentials Package (Dealer Provided)
PED	LPO, Premium Charging Package (Dealer Provided)
Q8E	Mechanical jack
RBR	Wheels, 22"
RCH	Wheels, 24"
RYK	LPO, GM J1772 AC Adapter
RYN	LPO, GM PowerShift AC Charging Adapter
RYW	LPO, GM CCS1 DC Adapter
RZU	LPO, Auxiliary Off-Road Lights
SB1	LPO, Flat splash guards
SDT	LPO, Trailer Hitch Holder
SL7	LPO, Utility Rack by Advantage, (dealer-installed)
SND	LPO, 24" (61 cm) Bright PVD wheels
SNY	LPO, 24" (61 cm) 6-Split-Spoke Aluminum Wheels in High Gloss Black
SUR	LPO, Trailer tire pressure monitor
TAU	Tail lamps
TRO	LPO, Trailer View Camera, wired
U05	Horn, dual note tone
UCV	Interior Camera
UIT	LED Reflective Windshield Collision Alert
UNW	LPO, Utility Wall U-Nut
VJQ	Recovery hooks, front
WJU	Denali Dark Package"""

d = {}
for line in lines.split('\n'):
    line = line.strip()
    if not line: continue
    code, desc = line.split('\t', 1)
    d[code.strip()] = desc.strip()

sierra_data = json.dumps(d, indent=2)

with open('frontend/views/partials/modules.js', 'r', encoding='utf-8') as f:
    c = f.read()

sierra_decl = "\nconst sierraevRpo = " + sierra_data + ";\n\nmodule.exports ="
c = c.replace("module.exports =", sierra_decl)
c = c.replace("  silveradoevRpo,\n}", "  silveradoevRpo,\n  sierraevRpo,\n}")

with open('frontend/views/partials/modules.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied to modules.js")
