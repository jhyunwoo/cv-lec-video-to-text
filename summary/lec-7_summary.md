제공해주신 강의 내용은 컴퓨터 비전의 특징점 검출(Feature Detection), 특히 **Harris Corner Detector의 심화 내용, Non-Maximal Suppression(NMS), 그리고 불변성(Invariance)과 스케일(Scale) 문제**를 다루고 있습니다.

주요 핵심 내용을 구조화하여 요약해 드립니다.

---

### 강의 내용 요약

#### 1. Harris Corner Detector의 수치적 최적화
*   **행렬 $M$의 분석:** 모든 에너지 행렬을 직접 계산하거나 근사화할 필요 없이, $M$ 행렬의 고유값($\lambda_1, \lambda_2$)만 분석하면 됨.
*   **고유값 분해의 생략 (Shortcut):** 고유값을 직접 구하는 연산은 비용이 크므로, 행렬식(Determinant)과 대각합(Trace)의 성질을 이용해 코너 응답(Corner Response, $R$) 점수를 계산함.
    *   $\det(M) = \lambda_1 \cdot \lambda_2 = AC - B^2$
    *   $\text{trace}(M) = \lambda_1 + \lambda_2 = A + D$
    *   **공식:** $R = \det(M) - k \cdot (\text{trace}(M))^2$ ($k$는 상수)
*   **$R$ 점수의 해석:**
    *   $\lambda_1, \lambda_2$ 모두 큼 $\rightarrow$ $R$ 값이 매우 큼 $\rightarrow$ **코너(Corner)**
    *   둘 중 하나만 큼 $\rightarrow$ $R$ 값이 작거나 음수 $\rightarrow$ **에지(Edge)**
    *   둘 다 작음 $\rightarrow$ $R$ 값이 작음 $\rightarrow$ **평탄한 영역(Flat)**

#### 2. Non-Maximal Suppression (NMS, 비최대 억제)
*   **문제점:** 실제 이미지에서는 코너 주변의 여러 픽셀이 모두 높은 $R$ 점수를 가져, 코너가 두껍게(Dense) 검출되는 현상 발생.
*   **해결책:** 일정 윈도우(예: $3 \times 3$) 내에서 국소 최대값(Local Maximum)을 가진 픽셀만 남기고 나머지는 억제(Suppress)함.
*   **과정:**
    1.  Thresholding: 특정 임계값 이상의 $R$ 점수를 가진 픽셀만 1차로 선별.
    2.  NMS 적용: 가장 대표적인(가장 값이 큰) 픽셀 하나만 선택하여 희소(Sparse)한 결과를 얻음.

#### 3. 특징점의 불변성(Invariance)과 공변성(Covariance)
*   **불변성(Invariance):** 입력이 변해도 출력(결과)이 변하지 않음.
*   **공변성(Covariance):** 입력이 변하면 출력도 그에 맞춰 예측 가능한 방식으로 변함.
*   **변환 유형별 특성:**
    *   **밝기(Intensity) 변화:**
        *   상수 더하기(Shift): 미분값 변화 없음 $\rightarrow$ **불변(Invariant)**
        *   상수 곱하기(Scaling): 미분값 변함 $\rightarrow$ 불변하지 않음
    *   **이동(Translation):** 위치는 공변(같이 이동함), 검출 여부는 불변.
    *   **회전(Rotation):** 고유값 기반 분석이므로 회전해도 고유값은 동일 $\rightarrow$ **불변(Invariant)**.
    *   **스케일(Scale/Zoom) 변화:** 줌인/줌아웃 시 코너가 에지처럼 보일 수 있음 $\rightarrow$ **불변하지 않음(Not Invariant)**. (가장 큰 문제)

#### 4. 스케일 불변성(Scale Invariance)과 Blob Detection
*   **스케일 문제 해결:** 하나의 윈도우 크기만으로는 다양한 크기의 코너를 모두 검출할 수 없음.
*   **접근법:** 다양한 크기의 윈도우(Scale)를 적용하여 반응값(Response)을 확인하고, 반응이 최대가 되는 스케일(Scale Signature)을 찾음. 이를 통해 서로 다른 스케일의 이미지에서도 동일한 특징점을 매칭할 수 있음("Up to scale").
*   **Blob Detector 도입:**
    *   코너보다 원형(Blob) 구조가 스케일 추정에 더 유리함.
    *   **LoG (Laplacian of Gaussian):** 가우시안의 2계 미분. "Mexican Hat" 모양의 필터로, 특정 크기의 Blob에 강하게 반응.
    *   **DoG (Difference of Gaussians):** LoG의 근사법. 서로 다른 표준편차($\sigma$)를 가진 두 가우시안의 차이를 이용하며, 연산량이 적어 효율적임.