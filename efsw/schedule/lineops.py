from efsw.schedule import models


def get_previous_pp(program_position):
    return get_previous_pp_by_time(program_position.lineup, program_position.dow, program_position.start_time)


def get_previous_pp_by_time(lineup, dow, start_time):
    if start_time == lineup.start_time:
        return None
    else:
        return lineup.program_positions.get(dow=dow, end_time=start_time)


def get_next_pp(program_position):
    return get_next_pp_by_time(program_position.lineup, program_position.dow, program_position.end_time)


def get_next_pp_by_time(lineup, dow, end_time):
    if end_time == lineup.end_time:
        return None
    else:
        return lineup.program_positions.get(dow=dow, start_time=end_time)


def get_similar_pp(program_position):
    return models.ProgramPosition.objects.filter(
        lineup=program_position.lineup,
        start_time=program_position.start_time,
        end_time=program_position.end_time,
        locked=program_position.locked,
        program=program_position.program,
    ).exclude(dow=program_position.dow)


def pp_is_empty(pp):
    return not pp.program and not pp.comment and not pp.locked