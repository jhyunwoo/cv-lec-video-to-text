제공해주신 강의 내용을 바탕으로 주요 핵심 내용과 개념을 구조화하여 한국어로 요약해 드립니다.

---

### 강의 요약: 컴퓨터 비전 (Harris Corner Detector & Feature Detection)

#### 1. Harris Corner Detector의 구현 및 최적화
*   **에너지 행렬(E)의 근사:** 모든 픽셀에 대해 에너지 행렬을 직접 계산하거나 그릴 필요 없이, 수평($I_x$) 및 수직($I_y$) 그라디언트의 합으로 구성된 **M 행렬**만 분석하면 됨.
*   **고유값(Eigenvalue) 분석:** M 행렬의 고유값($\lambda_1, \lambda_2$)을 통해 해당 영역의 특성을 파악 가능.
    *   $\lambda_1, \lambda_2$ 모두 큼: **코너 (Corner)**
    *   하나만 큼: **에지 (Edge)**
    *   모두 작음: **평탄한 영역 (Flat region)**
*   **연산 효율화 (R Score):** 고유값 분해를 직접 수행하는 대신, 행렬식(Determinant)과 대각합(Trace)을 이용한 **R 점수(Corner Response)** 공식을 사용.
    *   공식: $R = Det(M) - k \cdot (Trace(M))^2$
    *   $Det(M) = \lambda_1 \cdot \lambda_2$, $Trace(M) = \lambda_1 + \lambda_2$
    *   두 고유값이 모두 클 때만 R 값이 매우 커지므로 코너를 식별할 수 있음.

#### 2. Non-Maximum Suppression (NMS, 비최대 억제)
*   **필요성:** 코너 주변의 픽셀들은 모두 높은 R 점수를 가질 수 있어, 코너가 두껍거나 여러 개로 중복 검출되는 문제가 발생(Dense).
*   **작동 원리:** 특정 윈도우(예: 3x3) 내에서 **가장 큰 R 값을 가진 픽셀(Local Maximum)만 남기고** 나머지는 억제함.
*   **결과:** 중복된 점들을 제거하고 가장 대표적인 코너 포인트 하나만 희소하게(Sparse) 남김.
*   **Thresholding:** NMS 적용 전후에 일정 임계값(Threshold) 이상의 R 점수를 가진 픽셀만 코너로 간주 (임계값은 사용자가 설정).

#### 3. 불변성(Invariance)과 공변성(Covariance)
*   **정의:**
    *   **불변성(Invariance):** 입력이 변해도 출력이 변하지 않음.
    *   **공변성(Covariance):** 입력의 변화에 따라 출력도 예측 가능한 방식으로 함께 변함.
*   **Harris Detector의 특성:**
    *   **밝기 이동(Intensity Shift):** 불변함 (덧셈 연산은 그라디언트에 영향 없음).
    *   **밝기 스케일링(Intensity Scaling):** 불변하지 않음 (곱셈 연산은 그라디언트 크기를 변화시킴).
    *   **회전(Rotation):** **불변함 (Invariant).** 코너가 회전해도 고유값(타원의 형태)은 변하지 않음.
    *   **스케일(Scale/Zoom):** **불변하지 않음 (Not Invariant).** 이미지를 확대하면 뾰족한 코너가 완만한 에지처럼 보일 수 있어 감지되지 않음.

#### 4. 스케일 불변성(Scale Invariance)과 Blob Detection
*   **스케일 문제:** 동일한 코너라도 이미지의 확대/축소 비율에 따라 적절한 윈도우 크기가 달라져야 함.
*   **해결책:** 다양한 윈도우 크기(Scale)에서 반응(Response)을 측정하여, 반응이 최대가 되는 스케일을 찾음 (Scale Signature).
*   **Blob Detector:**
    *   코너보다 스케일(크기) 변화를 감지하기에 더 적합한 형태인 원형(Blob)을 검출.
    *   **LoG (Laplacian of Gaussian):** 가우시안의 2차 미분 형태로, "Mexican Hat" 모양의 필터. 특정 크기의 Blob에 강하게 반응함.
    *   **DoG (Difference of Gaussians):** LoG를 근사하기 위해 서로 다른 스케일의 두 가우시안의 차이를 이용하는 방법 (연산 효율성 높음).

#### 5. 기타 공지 사항
*   과제 1(Homework 1)은 이번 주 목요일 마감 예정.
*   과제 2(Homework 2) 곧 공개 예정.