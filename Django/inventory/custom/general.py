FWD_OR_REV = (
    ('f', 'FWD'),
    ('r', 'REV'),
)

CHECK_STATES = (
    (0, 'Not required'),
    (1, 'Pending'),
    (2, 'Correct')
)

LIGATION_STATES = (
    (0, 'Waiting parts or supplies'),
    (1, 'Ligated'),
    (2, 'Ligate - Low priority'),
    (3, 'Ligate - Mid priority'),
    (4, 'Ligate - High priority')
)

# bootstrap defaults
COLORS = (
    ('primary', 'Blue'),
    ('secondary', 'Gray'),
    ('success', 'Green'),
    ('info', 'Cyan'),
    ('warning', 'Yellow'),
    ('danger', 'Red'),
    ('light', 'White'),
    ('dark', 'Black'),
)