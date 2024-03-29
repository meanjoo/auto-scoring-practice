import cv2 as cv
import sys
import copy

'''
* python 반복자
python에서 어떤 타입/클래스가 iterable하다는 것은 for ... in문을 통해 반복될 수 있다는 것이다.
iterable한 타입은 __iter__ 메소드와 __next__ 메소드를 가지고 있다.
__iter__는 iterator를 반환한다. 
iterator는 __next__ 메소드로 어떤 컨테이너의 개별 요소를 반복하게 해준다.
__next__는 다음 반복 요소를 반환하고 더 이상 반환할 요소가 없으면 StopIteration 예외를 발생시킨다.
'''

class Point:
    def __init__(self, x ,y):
        self.x = x
        self.y = y

class Rect:
    def __init__(self, rect):
        self.x = rect[0]
        self.y = rect[1]
        self.w = rect[2]
        self.h = rect[3]

    def __iter__(self):
        self.i = -1
        return self
    
    def __next__(self):
        r = (self.x, self.y, self.w, self.h)
        self.i += 1
        if self.i >= 4:
            raise StopIteration
        return r[self.i]

    def __repr__(self):
        return repr((self.x, self.y, self.w, self.h))
    
    def __add__(self, other):
        return (self.x + other.x, self.y + other.y, self.w + other.w, self.h + other.h)
    
    def isSame(self, other):
        return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h

# def is_rect_intersect(rect1, rect2):
#     minx = min(rect1.x, rect2.x)
#     miny = min(rect1.y, rect2.y)
#     maxx = max(rect1.x + rect1.w, rect2.x + rect2.w)
#     maxy = max(rect1.y + rect1.h, rect2.y + rect2.h)

#     if maxx - minx <= rect1.w + rect2.w and maxy - miny <= rect1.h + rect2.h:
#         return True
#     return False

# def is_rect_near_included(rect1, rect2):
#     pass

# def minimum_area_contain_two_rects(rect1, rect2):
#     leftTop = Point(min(rect1.x, rect2.x), min(rect1.y, rect2.y))
#     rightBottom = Point(max(rect1.x + rect1.w, rect2.x + rect2.w), max(rect1.y + rect1.h, rect2.y + rect2.h))

#     return Rect((leftTop.x, leftTop.y, rect1.w + rect2.w - (rightBottom.x - leftTop.x), rect1.h + rect2.h - (rightBottom.y - leftTop.y)))

path = './test_image'
img = cv.imread(path+'/newsample.jpeg')
# img = cv.imread(path+'/sample.jpeg')

if img is None:
    sys.exit('Could not read the image.')

img1 = img.copy()
img2 = img.copy()
img3 = img.copy()

img4 = img.copy()


cv.namedWindow('image', cv.WINDOW_NORMAL)
cv.imshow('image', img)

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# cv.threshold(흑백 이미지, 임계값, 임계값 만족 시 적용할 값(value), 타입)
# 타입-THRESH_BINARY: 흑백 이미지의 픽셀 값이 임계값을 넘으면 value로 지정하고 넘지 못하면 0으로 지정
#     -THRESH_BINARY_INV: 위와 반대
border, binary = cv.threshold(gray, 100, 255, cv.THRESH_BINARY) # 흑백 이미지 이진화 (0: 검은색, 255: 흰색)

# blur = cv.GaussianBlur(gray, (3,3),0)
canny = cv.Canny(binary, 100, 200)

row, col = 6,2
contours, hier = cv.findContours(canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
# rects = [cv.boundingRect(each) for each in contours] # 사각형 정보 튜플(x,y,w,h)을 원소로 하는 리스트
rects = [Rect(cv.boundingRect(each)) for each in contours] # cv.boundingRect(each)는 사각형 정보 튜플(x,y,w,h)을 반환
rects.sort(key=lambda rect : (rect.x, rect.y, rect.w, rect.w))

crop, cropAll = [], [] # 세로 분할, 세로 분할 된 거에서 가로 분할<-한 문항으로 분할

# 세로로 자르기
for rect in rects:
    tmp = (int)(rect.w / col)
    for c in range(col):
        crop.append(Rect((rect.x + tmp*c, rect.y, tmp, rect.h)))

# 가로로 자르기
for rect in crop:
    tmp = (int)(rect.h / row)
    for r in range(row):
        cropAll.append(Rect((rect.x, rect.y + tmp*r, rect.w, tmp)))

result, extract = [], []
offset = 10 # hwptable은 5로
for rect in cropAll:
    sx = rect.x + offset
    sy = rect.y + offset
    ex = rect.x + rect.w - offset
    ey = rect.y + rect.h - offset
    # 보는 영역
    cv.rectangle(img2, (sx, sy), (ex, ey), (0,255,0), 2)
    
    croped_img = canny[sy:ey, sx:ex]
    contours, heir = cv.findContours(croped_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE) # contours는 numpy.ndarray
    tmp = [Rect(cv.boundingRect(each)) for each in contours]
    for t in tmp:
        t.x += (rect.x + offset)
        t.y += (rect.y + offset)
    result.extend(tmp)
    result.append(Rect((-1,-1,-1,-1)))
    
    # 포함 관계 판단 : 얘 뭐지?
    tmp.sort(key=lambda rect : (rect.x, rect.y, rect.w, rect.w))
    idx = 0
    while idx < len(tmp)-1:
        ix1 = max(tmp[idx].x, tmp[idx+1].x)
        iy1 = max(tmp[idx].y, tmp[idx+1].y)
        ix2 = min(tmp[idx].x+tmp[idx].w, tmp[idx+1].x+tmp[idx+1].w)
        iy2 = min(tmp[idx].y+tmp[idx].h, tmp[idx+1].y+tmp[idx+1].h)

        ir = Rect((ix1, iy1, ix2-ix1, iy2-iy1))
        if tmp[idx].isSame(ir):
            # 포함되는 사각형 중 큰 사각형만 idx번째에 남기기
            tmp[idx] = tmp[idx+1]
            tmp.pop(idx+1)
        elif tmp[idx+1].isSame(ir):
            tmp.pop(idx+1)
        else:
            idx += 1
    extract.extend(tmp)
    extract.append(Rect((-1,-1,-1,-1)))


cropAll.sort(key=lambda rect : (rect.x, rect.y, rect.w, rect.w))
print('==crop==')
print(crop)
print('==cropAll==')
print(cropAll)

area = [rect.w*rect.h for rect in rects]
area.sort()
print('==area==')
print(area)

# 가장 바깥 사각형
for rect in rects:
    color = (0,255,0)
    cv.rectangle(img1, (rect.x, rect.y),
            (rect.x + rect.w, rect.y + rect.h), color, 2)

print('==result==')
print(result)
print(type(result[0]))

print('==extract==')
print(extract)
print(type(extract[0]))

# 숫자 찾기, img3
for rect in result:
    if (rect.x == -1): continue
    color = (0,255,0)
    cv.rectangle(img3, (rect.x, rect.y),
            (rect.x + rect.w, rect.y + rect.h), color, 2)

# img4 그리기
for rect in extract:
    if (rect.x == -1): continue
    color = (255,0,255)
    cv.rectangle(img4, (rect.x, rect.y),
            (rect.x + rect.w, rect.y + rect.h), color, 2)
    
# box 저장
# 손실 최소화 -> 기존 크기의 max(x,y)를 한 변으로 하는 정사각형으로 흰 배경을 resize하고 그 위에 숫자 합성(이미지 연산) -> 28,28로 resize
# 바로 28,28로 resize 하면 비율이 이상해짐
savepath = './save_test'
whiteBg = cv.imread(path + '/white_bg.jpg', cv.IMREAD_GRAYSCALE)

# 크기 다른 이미지 합성
# https://yeko90.tistory.com/entry/opencv-%EB%91%90-%EC%9D%B4%EB%AF%B8%EC%A7%80-%ED%95%A9%EC%B9%98%EB%8A%94-%EB%B0%A9%EB%B2%95-%ED%81%AC%EA%B8%B0-%EB%8B%A4%EB%A5%B8-%EC%9D%B4%EB%AF%B8%EC%A7%80
for i in range(len(extract)):
    if (extract[i].x == -1):
        cv.imwrite(savepath + '/newsquare28img' + str(i) + '.jpg', cv.resize(whiteBg, (28,28), interpolation=cv.INTER_AREA))
        continue

    target = binary[extract[i].y:extract[i].y+extract[i].h, extract[i].x:extract[i].x+extract[i].w] # 사각형 영역 추출
    mask = 255 - target
    sz = (int)(max(extract[i].w, extract[i].h) * 1.5)
    squareimg = cv.resize(whiteBg.copy(), dsize=(sz,sz)) # +1 해준 건 밑에 sx, sy 연산에서 int로 변하면서 범위에 문제 생길까봐?

    # print(target.shape[:2], extract[i].h, extract[i].w)
    # squareimg 중심: (sz/2, sz/2)
    # img의 시작점: (sz/2 - w/2, sz/2 - h/2)
    # sx = (int)((extract[i].h - extract[i].w) / 2) if extract[i].h >= extract[i].w else 0
    # sy = (int)((extract[i].w- extract[i].h) / 2) if extract[i].w >= extract[i].h else 0
    sx = (int)(sz/2 - extract[i].w/2)
    sy = (int)(sz/2 - extract[i].h/2)
    crop = squareimg[sy:sy+extract[i].h, sx:sx+extract[i].w]
    cv.copyTo(target, mask, crop)

    # cv.imwrite(savepath + '/squareimg' + str(i) + '.jpg', squareimg)
    cv.imwrite(savepath + '/newsquareimg' + str(i) + '.jpg', squareimg)


    # python opencv에서 img.shape를 통해 이미지 크기를 알 수 있다. tuple-(height, weight) <- 흑백 이미지
    # 컬러 이미지면 채널도 가져온다. (height, weight, channel)
    if squareimg.shape[0] > 28: # 이미지 축소 - INTER_AREA
        squareimg = cv.resize(squareimg, (28,28), interpolation=cv.INTER_AREA)
    elif squareimg.shape[0] < 28: # 이미지 확대 - INTER_LINEAR(default, slow) / INTER_CUBIC(linear보다 느리지만 품질 굿)
        squareimg = cv.resize(squareimg, (28,28), interpolation=cv.INTER_LINEAR)
    # cv.imwrite(savepath + '/square28img' + str(i) + '.jpg', squareimg)
    cv.imwrite(savepath + '/newsquare28img' + str(i) + '.jpg', squareimg)

    # cv.imwrite(savepath + '/square28img_inv' + str(i) + '.jpg', 255-squareimg) # 지금 저장된 건 흰 배경에 검은 글씬데 검은 배경에 흰 글씨로 하고 싶으면 이렇게 저장



k = cv.waitKey(0)

if k == 27:
    cv.destroyAllWindows()
elif k == ord('s'):
    cv.imwrite('contourTest.jpg', img1)
    cv.imwrite('contourTest2.jpg', img2)
    cv.imwrite('contourTest3.jpg', img3)

    cv.imwrite('contourTest4.jpg', img4)
    
    cv.destroyAllWindows()