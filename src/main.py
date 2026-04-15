import sys
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
matplotlib.rc('font', family='sans-serif')

from PyQt6.QtWidgets import QApplication

from ui import AnalyXMainWindow


def main():
    app = QApplication(sys.argv)
    window = AnalyXMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
