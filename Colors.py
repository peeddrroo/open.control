#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_MK2/Colors.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import object
from _Framework.ButtonElement import Color
# from .consts import BLINK_LED_CHANNEL, PULSE_LED_CHANNEL

class Blink(Color):

    def __init__(self, midi_value = 0, *a, **k):
        super(Blink, self).__init__(midi_value, *a, **k)

    def draw(self, interface):
        interface.send_value(0)
        interface.send_value(self.midi_value, channel=13)


class Pulse(Color):

    def __init__(self, midi_value = 0, *a, **k):
        super(Pulse, self).__init__(midi_value, *a, **k)

    def draw(self, interface):
        interface.send_value(0)
        interface.send_value(self.midi_value, channel=14)


class Rgb(object):
    BLACK = Color(0)
    DARK_GREY = Color(1)
    GREY = Color(2)
    WHITE = Color(3)
    RED = Color(127)
    RED_BLINK = Blink(127)
    RED_PULSE = Pulse(127)
    RED_HALF = Color(107)
    ORANGE = Color(3)
    ORANGE_HALF = Color(3)
    AMBER = Color(96)
    AMBER_HALF = Color(14)
    YELLOW = Color(4)
    YELLOW_HALF = Color(4)
    DARK_YELLOW = Color(4)
    DARK_YELLOW_HALF = Color(4)
    GREEN = Color(126)
    GREEN_BLINK = Blink(126)
    GREEN_PULSE = Pulse(126)
    GREEN_HALF = Color(126)
    MINT = Color(29)
    MINT_HALF = Color(31)
    LIGHT_BLUE = Color(37)
    LIGHT_BLUE_HALF = Color(39)
    BLUE = Color(125)
    BLUE_BLINK = Blink(125)
    BLUE_HALF = Color(125)
    DARK_BLUE = Color(125)
    DARK_BLUE_HALF = Color(51)
    PURPLE = Color(53)
    PURPLE_HALF = Color(55)
    DARK_ORANGE = Color(84)


LIVE_COLORS_TO_MIDI_VALUES = {16749734	:	0	,
16753961	:	1	,
13408551	:	2	,
16249980	:	3	,
12581632	:	4	,
1769263	:	5	,
2490280	:	6	,
6094824	:	7	,
9160191	:	8	,
5538020	:	9	,
9611263	:	10	,
14183652	:	11	,
15029152	:	12	,
16777215	:	13	,
16725558	:	14	,
16149507	:	15	,
10056267	:	16	,
16773172	:	17	,
8912743	:	18	,
4047616	:	19	,
49071	:	20	,
1698303	:	21	,
1090798	:	22	,
32192	:	23	,
8940772	:	24	,
11958214	:	25	,
16726484	:	26	,
13684944	:	27	,
14837594	:	28	,
16753524	:	29	,
13872497	:	30	,
15597486	:	31	,
13821080	:	32	,
12243060	:	33	,
10208397	:	34	,
13958625	:	35	,
13496824	:	36	,
12173795	:	37	,
13482980	:	38	,
11442405	:	39	,
15064289	:	40	,
11119017	:	41	,
13013643	:	42	,
12026454	:	43	,
10060650	:	44	,
12565097	:	45	,
10927616	:	46	,
8237133	:	47	,
8962746	:	48	,
10204100	:	49	,
8758722	:	50	,
8623052	:	51	,
10851765	:	52	,
12558270	:	53	,
12349846	:	54	,
8092539	:	55	,
11481907	:	56	,
11096369	:	57	,
7491393	:	58	,
14402304	:	59	,
8754719	:	60	,
5480241	:	61	,
695438	:	62	,
2319236	:	63	,
1716118	:	64	,
3101346	:	65	,
6441901	:	66	,
10701741	:	67	,
13381230	:	68	,
3947580	:	69}




RGB_COLOR_TABLE = ((	0	,	16749734	)	,
(	1	,	16753961	)	,
(	2	,	13408551	)	,
(	3	,	16249980	)	,
(	4	,	12581632	)	,
(	5	,	1769263	)	,
(	6	,	2490280	)	,
(	7	,	6094824	)	,
(	8	,	9160191	)	,
(	9	,	5538020	)	,
(	10	,	9611263	)	,
(	11	,	14183652	)	,
(	12	,	15029152	)	,
(	13	,	16777215	)	,
(	14	,	16725558	)	,
(	15	,	16149507	)	,
(	16	,	10056267	)	,
(	17	,	16773172	)	,
(	18	,	8912743	)	,
(	19	,	4047616	)	,
(	20	,	49071	)	,
(	21	,	1698303	)	,
(	22	,	1090798	)	,
(	23	,	32192	)	,
(	24	,	8940772	)	,
(	25	,	11958214	)	,
(	26	,	16726484	)	,
(	27	,	13684944	)	,
(	28	,	14837594	)	,
(	29	,	16753524	)	,
(	30	,	13872497	)	,
(	31	,	15597486	)	,
(	32	,	13821080	)	,
(	33	,	12243060	)	,
(	34	,	10208397	)	,
(	35	,	13958625	)	,
(	36	,	13496824	)	,
(	37	,	12173795	)	,
(	38	,	13482980	)	,
(	39	,	11442405	)	,
(	40	,	15064289	)	,
(	41	,	11119017	)	,
(	42	,	13013643	)	,
(	43	,	12026454	)	,
(	44	,	10060650	)	,
(	45	,	12565097	)	,
(	46	,	10927616	)	,
(	47	,	8237133	)	,
(	48	,	8962746	)	,
(	49	,	10204100	)	,
(	50	,	8758722	)	,
(	51	,	8623052	)	,
(	52	,	10851765	)	,
(	53	,	12558270	)	,
(	54	,	12349846	)	,
(	55	,	8092539	)	,
(	56	,	11481907	)	,
(	57	,	11096369	)	,
(	58	,	7491393	)	,
(	59	,	14402304	)	,
(	60	,	8754719	)	,
(	61	,	5480241	)	,
(	62	,	695438	)	,
(	63	,	2319236	)	,
(	64	,	1716118	)	,
(	65	,	3101346	)	,
(	66	,	6441901	)	,
(	67	,	10701741	)	,
(	68	,	13381230	)	,
(	69	,	3947580	))
