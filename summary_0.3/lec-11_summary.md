제공된 강의 내용은 컴퓨터 비전의 **이미지 분할(Segmentation)**, **멀티뷰(Multi-view) 기하학**, 그리고 **이미지 변환(Transformation)**에 대한 핵심 개념들을 다루고 있습니다. 주요 내용을 요약하면 다음과 같습니다.

### 1. 이미지 분할과 특징 공간 (Image Segmentation & Feature Space)
*   **기존 K-means의 한계:** 단순히 픽셀의 강도(Intensity)만 사용할 경우, 공간적 인접성(Spatial smoothness)을 보장하지 못함.
*   **특징 공간의 확장:**
    *   단순 밝기값뿐만 아니라 **위치 정보(X, Y 좌표)**, **색상(RGB)**, **텍스처(Texture)** 등을 결합하여 특징 벡터(Feature vector)를 구성해야 함.
    *   이를 통해 픽셀 값이 비슷하면서도 물리적으로 가까운 픽셀들을 그룹화(Segmentation)할 수 있음.

### 2. 멀티뷰와 정렬 (Multi-view & Alignment)
*   **멀티뷰의 필요성:** 단일 이미지만으로는 알 수 없는 객체의 **깊이(Depth)**와 **3D 형상**을 파악하기 위해 여러 시점의 이미지가 필요함.
*   **정렬(Alignment) 문제:**
    *   동일한 객체를 다른 시점에서 찍은 두 이미지 사이의 대응점(Correspondence)을 찾는 과정 (예: SIFT 매칭 활용).
    *   한 이미지의 좌표를 다른 이미지의 좌표로 매핑해주는 **변환 함수(Transformation function)**의 파라미터를 찾는 것이 목표.

### 3. 이미지 변환의 종류 (Types of Transformations)
*   **기본 변환:** 이동(Translation), 회전(Rotation), 크기 조절(Scaling), 전단(Shear), 원근 변환(Perspective) 등이 있음.
*   **행렬 표현 (Matrix Representation):**
    *   선형 변환(Linear Transformation)은 $2 \times 2$ 행렬로 표현 가능 (Scaling, Rotation, Shear, Mirroring).
    *   **문제점:** $2 \times 2$ 행렬로는 **이동(Translation)**을 표현할 수 없음 ($Ax + B$ 형태가 불가능).

### 4. 동차 좌표계와 아핀 변환 (Homogeneous Coordinates & Affine Transformation)
*   **동차 좌표계 (Homogeneous Coordinates):**
    *   이동(Translation)을 행렬 곱으로 표현하기 위해 좌표 차원을 하나 늘림 ($(x, y) \rightarrow (x, y, 1)$).
    *   이를 통해 $3 \times 3$ 행렬을 사용하여 이동을 포함한 모든 변환을 통일된 방식으로 처리 가능.
*   **아핀 변환 (Affine Transformation):**
    *   선형 변환과 이동의 결합.
    *   **특징:** 변환 후에도 **평행선은 평행하게 유지됨**.
    *   **파라미터 추정:** 최소 **3개의 선형 독립(Linearly independent)**인 대응점 쌍이 있어야 파라미터(6개)를 구할 수 있음.

### 5. 투영 변환과 이미지 모자이크 (Projective Transformation & Image Mosaicking)
*   **투영 변환 (Projective Transformation / Homography):**
    *   가장 복잡한 변환 형태로, 아핀 변환과 달리 **평행선이 유지되지 않음** (원근감 발생).
    *   3D 공간에서 카메라 중심(Center of projection)을 기준으로 투영면이 바뀌는 것으로 이해할 수 있음.
*   **이미지 모자이크 (Panorama):**
    *   서로 다른 각도에서 찍은 이미지들을 하나의 기준 평면(Reference plane)으로 변환(Warping)하여 이어 붙이는 기술.
    *   이를 위해 **호모그래피(Homography)** 행렬을 계산하여 픽셀 좌표를 변환해야 함.