import statistics


def calculate_variability(reaction_times: list[float]) -> float:
    """
    Рассчитывает вариативность как стандартное отклонение времени реакции.
    Возвращает 0, если данных меньше двух.
    """
    if len(reaction_times) < 2:
        return 0.0
    return statistics.stdev(reaction_times)


def calculate_accuracy(results: dict, total_stimuli: int) -> float:
    """
    Рассчитывает общую точность в процентах.
    Точность = (Правильные действия / Всего стимулов) * 100
    Правильные действия = (Всего стимулов - Все ошибки)
    """
    if total_stimuli == 0:
        return 0.0
    
    total_errors = results.get("missed_go", 0) + results.get("false_alarms", 0)
    correct_actions = total_stimuli - total_errors
    
    return (correct_actions / total_stimuli) * 100
