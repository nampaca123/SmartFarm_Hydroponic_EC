## Repository Guide

**※ 레포지토리 안내 ※ Repository Guide**

## Project Description

이 프로그램은 제가 스마트팜 학회에서 활동했던 당시 참여했었던 프로젝트의 결과물로, 사용자가 입력한 작물 (겨자채, 근대, 상추, 케일에 대한 시스템이 구현되어 있음) 에 대해 수경재배에 필요한 정보를 제공합니다. AI HUB에서 추출하여 가공한 데이터를 기반으로 각각의 작물에 적합한 양액의 EC값, 실내 온도, 광량, 양액의 온도, pH값 등을 제공합니다. 또한 식물이 자라는 배지의 배지 EC 측정 센서와, 배지 외부의 양액 EC 측정 센서에서 EC값을 지속적으로 측정하여, 해당 측정값을 바탕으로 현 환경에서 작물이 얼마만큼의 양분을 흡수할 수 있는가에 대한 데이터를 제공합니다.

This program is the result of a project I participated in during my time with the Smart Farm academic society. It provides essential information for hydroponic cultivation of specific crops (currently implemented for mustard greens, Swiss chard, lettuce, and kale). The system delivers data such as the optimal nutrient solution EC values, indoor temperature, light intensity, nutrient solution temperature, and pH values, all based on processed data extracted from AI HUB.

Additionally, the system continuously measures EC values using sensors placed both in the growing medium and in the external nutrient solution. This data allows for an assessment of nutrient absorption by the crops under current conditions.


## Contributions

이 프로젝트에서, 저는 아두이노 EC 센서로부터 전달받은 데이터의 입출력과 데이터베이스 운영에 대한 업무를 맡았습니다. 데이터베이스는 SQLite3를 기반으로 구축되었고, Flask의 g 개체를 통해 시스템 내에서 운용됩니다. 서로 작업한 내역을 합병 했을 때 발생한 쓰레드 충돌 문제 등 여러 돌발상황에 대처하고, 성공적인 통합 시스템을 구축해가는 과정을 커밋 기록을 통해 확인할 수 있습니다.

In this project, I was responsible for managing the input and output of data from the Arduino EC sensor and the operation of the database. The database is built on SQLite3 and is operated within the system through Flask's `g` object. I handled various unexpected issues, such as thread conflict problems that arose when merging different parts of the project, ensuring the successful integration of the overall system. These efforts and processes can be tracked through the commit history.
