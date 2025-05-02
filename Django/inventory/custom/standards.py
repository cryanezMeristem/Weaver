from Bio.Restriction.Restriction_Dictionary import rest_dict

bsai = rest_dict["BsaI"] or None
bsmbi = rest_dict["BsmBI"] or None
sapi = rest_dict["SapI"] or None

assembly_standards = {
    'ytk': {
        'name': 'Yeast Toolkit',
        'family': 'golden_gate',
        'enzymes': {
            0: 'bsmbi',
            1: 'bsai',
            2: 'bsmbi',
        },
        'domestication': {
            'enzyme': bsmbi,
            'receiver': {
                'name': 'L0R-GFP',
                'ohs': {
                    'oh5': 'CTCC',
                    'oh3': 'CGAG'
                },
            },
            'enzymes': [
                'bsmbi',
                'bsai',
            ],
        },
        'ohs': {
            'l0': {
                '81': {
                    'name': '8-1',
                    'oh': 'CCCT'
                },
                '12': {
                    'name': '1-2',
                    'oh': 'AACG'
                },
                '23': {
                    'name': '2-3',
                    'oh': 'TATG'
                },
                '3a3b': {
                    'name': '3a-3b',
                    'oh': 'TTCT',
                    'prev_bases': 'gg'
                },
                '34': {
                    'name': '3-4',
                    'oh': 'ATCC'
                },
                '4a4b': {
                    'name': '4a-4b',
                    'oh': 'TGGC'
                },
                '45': {
                    'name': '4-5',
                    'oh': 'GCTG'
                },
                '56': {
                    'name': '5-6',
                    'oh': 'TACA'
                },
                '67': {
                    'name': '6-7',
                    'oh': 'GAGT'
                },
                '78': {
                    'name': '7-8',
                    'oh': 'CCGA'
                },
                '8a8b': {
                    'name': '8a-8b',
                    'oh': 'CAAT'
                },
            },
            'l1': {
                'S': {
                    'name': 'S',
                    'oh': 'CTGA'
                },
                '1': {
                    'name': '1',
                    'oh': 'CCAA'
                },
                '2': {
                    'name': '2',
                    'oh': 'GATG'
                },
                '3': {
                    'name': '3',
                    'oh': 'GTTC'
                },
                '4': {
                    'name': '4',
                    'oh': 'GGTA'
                },
                '5': {
                    'name': '5',
                    'oh': 'AAGT'
                },
                'E': {
                    'name': 'E',
                    'oh': 'AGCA'
                },
            },
        },
    },
    'loop': {
        'name': 'Loop',
        'family': 'golden_gate',
        'enzymes': {
            0: 'sapi',
            1: 'bsai',
            2: 'sapi',
            3: 'bsai',
            4: 'sapi',
        },
        'domestication': {
            'enzyme': sapi,
            'receiver': {
                'name': 'pL0R-mRFP1',
                'ohs': {
                    'oh5': 'TCC',
                    'oh3': 'CGA'
                },
            },
            'enzymes': [
                'aari',
                'bsai',
                'sapi'
            ],
        },
        'ohs': {
            'l0': {
                'a': {
                    'name': 'A',
                    'oh': 'GGAG'
                },
                'b': {
                    'name': 'B',
                    'oh': 'TACT'
                },
                'c': {
                    'name': 'C',
                    'oh': 'AATG'
                },
                'd': {
                    'name': 'D',
                    'oh': 'AGGT',
                    'prev_bases': 'tc'
                },
                'e': {
                    'name': 'E',
                    'oh': 'GCTT',
                    'prev_bases': 'tc'
                },
                'f': {
                    'name': 'F',
                    'oh': 'CGCT'
                },
            },
            'l1': {
                'alpha': {
                    'name': 'GAMMA',
                    'oh': 'ATG'
                },
                'beta': {
                    'name': 'BETA',
                    'oh': 'GCA'
                },
                'gamma': {
                    'name': 'GAMMA',
                    'oh': 'TAC'
                },
                'epsilon': {
                    'name': 'EPSILON',
                    'oh': 'CAG'
                },
                'omega': {
                    'name': 'OMEGA',
                    'oh': 'GGT'
                },
            },
        },
    },
    'gb': {
        'name': 'Golden Braid 2.0',
        'family': 'golden_gate',
        'enzymes': {
            0: 'bsmbi',
            1: 'bsai',
            2: 'bsmbi',
        },
        'domestication': {
            'enzyme': bsmbi,
            'receiver': {
                'name': 'pUPD',
                'ohs': {
                    'oh5': 'CTCG',
                    'oh3': 'TGAG'
                },
            },
            'enzymes': [
                'bsai',
                'btgzi',
                'bsmbi'
            ],
        },
        'ohs': {
            'l0': {
                'a1_5': {
                    'name': 'A1 5\'',
                    'oh': 'GGAG'
                },
                'a2_5': {
                    'name': 'A2 5\'',
                    'oh': 'TGAC'
                },
                'a3_5': {
                    'name': 'A3 5\'',
                    'oh': 'TCCC'
                },
                'b1_5': {
                    'name': 'B1 5\'',
                    'oh': 'TACT'
                },
                'b2_5': {
                    'name': 'B2 5\'',
                    'oh': 'CCAT'
                },
                'b3_5': {
                    'name': 'B3 5\'',
                    'oh': 'AATG'
                },
                'b4_5': {
                    'name': 'B4 5\'',
                    'oh': 'AGCC',
                    'prev_bases': 'tc'
                },
                'b5_5': {
                    'name': 'B5 5\'',
                    'oh': 'TTCG',
                    'prev_bases': 'tc'
                },
                'b6_5': {
                    'name': 'B6 5\'',
                    'oh': 'GCTT',
                    'prev_bases': 'tc'
                },
                'c1_5': {
                    'name': 'C1 5\'',
                    'oh': 'GGTA'
                },
                'c1_3': {
                    'name': 'C1 3\'',
                    'oh': 'CGCT'
                },
            },
            'l1': {
            },
        },
    },
}
