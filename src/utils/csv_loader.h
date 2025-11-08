#ifndef CSV_LOADER_H
#define CSV_LOADER_H

#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include "../models/observation.h"

/**
 * @brief Класс для загрузки наблюдений из CSV файлов
 */
class CsvLoader {
public:
    /**
     * @brief Загружает наблюдения из CSV файла
     * @param filename Имя файла
     * @return Вектор наблюдений
     */
    static std::vector<Observation> loadObservations(const std::string& filename);
    
    /**
     * @brief Проверяет существование файла
     * @param filename Имя файла
     * @return true если файл существует, иначе false
     */
    static bool fileExists(const std::string& filename);
};

#endif // CSV_LOADER_H