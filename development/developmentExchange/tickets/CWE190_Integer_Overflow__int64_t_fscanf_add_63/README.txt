
1) Версия SVACE:3.1.1
2) Проект, в котором ошибка SVACE: набор тестов C/C++ Juliet v1.3.
3) Файл, в котором проявляется ошибка SVACE:
testcases/CWE190_Integer_Overflow/s01/CWE190_Integer_Overflow__int64_t_fscanf_add_63b.c
4) Строка на которой проявляется ошибка SVACE: 27

4) Описание ошибки SVACE: не выдано предупреждение на потенциальный дефект (неполнота)
5) Описание дефекта: ошибка переполнения при арифметических операциях.
6) Соответствующий тип дефектов SVACE: INTEGER_OVERFLOW.

P.S Svace 3.1.1. не выдал требуемую ошибку на всех CWE190,191 набора Juliet 1.3. , где переполнение
происходит в результате вычислений с переменной, полученой из другой функции. В чекере
не поддерживается межпроцедурность? (???)

Инструкция по сборке/проверке теста:
cd build
cmake ../
make




