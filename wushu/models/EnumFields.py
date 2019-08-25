import enum


class EnumFields(enum.Enum):
    class LEVELTYPE2(enum.Enum):
        VISA = 1
        GRADE = 2
        BELT = 3

    class BRANCH2(enum.Enum):
        TAOLU = 1
        SANDA = 2
        WUSHU = 3

    class COMPSTATUS(enum.Enum):
        PREREGISTRATIONOPEN = 1
        PREREGISTRATIONCLOSED = 2
        COMPLETED = 3

    class COMPTYPE(enum.Enum):
        NATIONAL = 1
        INTERNATIONAL = 2

    TAOLU = 'TAOLU'
    SANDA = 'SANDA'
    WUSHU = 'WUSHU'

    BRANCH = (
        (TAOLU, 'TAOLU'),
        (SANDA, 'SANDA'),
        (WUSHU, 'WUSHU'),
    )

    VISA = 'VISA'
    GRADE = 'GRADE'
    BELT = 'BELT'

    LEVELTYPE = (
        (VISA, 'VISA'),
        (GRADE, 'GRADE'),
        (BELT, 'BELT'),
    )
