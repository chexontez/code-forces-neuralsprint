import random
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QDateTime


class TestEngine(QObject):
    color_changed = pyqtSignal(str)
    test_started = pyqtSignal()
    test_finished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_go_stimulus)

        self.is_running = False
        self.stimulus_start_time = 0
        self.results = {}
        self.current_stimulus = "no-go"
        
        self.max_stimuli = 5
        self.stimuli_count = 0

    def start_test(self):
        if self.is_running:
            return

        self.is_running = True
        self.stimuli_count = 0
        self.results = {"reaction_times": [], "missed_go": 0, "false_alarms": 0}
        self.test_started.emit()

        self.color_changed.emit("red")
        self.current_stimulus = "no-go"
        self.schedule_next_go()

    def stop_test(self):
        if not self.is_running:
            return

        self.is_running = False
        self.timer.stop()

        # Если тест прервали, когда нужно было нажать, засчитываем пропуск
        if self.current_stimulus == "go":
            self.results["missed_go"] += 1

        self.color_changed.emit("white")
        self.test_finished.emit(self.results)

    def schedule_next_go(self):
        if not self.is_running or self.stimuli_count >= self.max_stimuli:
            if self.is_running:
                self.stop_test()
            return
        delay = random.randint(1000, 4000)
        self.timer.start(delay)

    def show_go_stimulus(self):
        if not self.is_running:
            return

        self.stimuli_count += 1
        self.color_changed.emit("green")
        self.current_stimulus = "go"
        self.stimulus_start_time = QDateTime.currentMSecsSinceEpoch()
        # Больше нет таймера, который сбрасывает зеленый цвет

    def record_reaction(self):
        if not self.is_running:
            return

        if self.current_stimulus == "go":
            reaction_time = QDateTime.currentMSecsSinceEpoch() - self.stimulus_start_time
            self.results["reaction_times"].append(reaction_time)
            print(f"Верное нажатие! Время реакции: {reaction_time} мс")

            # Сразу возвращаемся к красному и планируем следующий
            self.color_changed.emit("red")
            self.current_stimulus = "no-go"
            self.schedule_next_go()

        elif self.current_stimulus == "no-go":
            self.results["false_alarms"] += 1
            print("Ошибка! Нажатие на No-Go стимул (красный).")
