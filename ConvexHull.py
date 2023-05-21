# Mencari convex hull menggunakan algoritma Graham Scan
# Sumber : https://www.geeksforgeeks.org/convex-hull-using-graham-scan/

import math

class ConvexHull :
    @staticmethod
    def searchHull(coordinates, hull) :
        # Cari titik terendah dari kumpulan koordinat yang ada
        lowestPoint = coordinates[0]
        for i in range(1,len(coordinates)) :
            if (coordinates[i][1] < lowestPoint[1]) :
                lowestPoint = coordinates[i]
            elif (coordinates[i][1] == lowestPoint[1]) :
                if (coordinates[i][0] < lowestPoint[0]) :
                    lowestPoint = coordinates[i]
        coordinates.remove(lowestPoint)
        convexHull = [lowestPoint]

        # Urutkan semua titik berdasarkan sudut polar terhadap titik terendah
        coordinates = ConvexHull.__sortPolarAngle(lowestPoint,coordinates)

        # Hapus semua titik i yang segaris dengan titik i+1 kecuali yang terjauh
        m = 0
        for i in range(len(coordinates)-1) :
            if (ConvexHull.__searchOrientation(lowestPoint,coordinates[i],coordinates[i+1]) == 0) :
                continue
            coordinates[m] = coordinates[i]
            m += 1
        
        if (m < 2) :
            raise Exception()
        convexHull.append(coordinates[0])
        convexHull.append(coordinates[1])
        # Hapus semua titik yang orientasinya dengan next to top of stack dan top of stack tidak counterclockwise
        
        for i in range(2,m) :
            while (len(convexHull) > 1 and ConvexHull.__searchOrientation(convexHull[-2], convexHull[-1], coordinates[i]) != -1) :
                convexHull.pop()
            convexHull.append(coordinates[i])
        hull[:] = list(convexHull)
    
    @staticmethod
    def __pointDistance(a,b) :
        # Menghitung jarak euclidean antara titik a dan b
        return math.sqrt(pow(a[0]-b[0],2) + pow(a[1]-b[1],2))
    
    @staticmethod
    def __searchOrientation(a,b,c) :
        # Mencari orientasi 3 titik a,b,c
        # Sumber : https://iq.opengenus.org/orientation-of-three-ordered-points/
        slope = (b[1]-a[1]) * (c[0]-b[0]) - (c[1]-b[1]) * (b[0]-a[0])
        if (slope == 0) : # Collinear
            return 0
        elif (slope < 0) : # Counterclockwise
            return -1
        else : # Clockwise
            return 1
    
    @staticmethod
    def __comparePolarAngle(a,b,c) :
        # Membandingkan sudut polar titik b dan c terhadap titik a
        # Mengembalikan -1 jika sudut titik b lebih kecil dari titik c dan 1 jika sebaliknya
        orientation = ConvexHull.__searchOrientation(a,b,c)
        if orientation == 0 :
            if ConvexHull.__pointDistance(a,b) <= ConvexHull.__pointDistance(a,c) :
                return -1
            else :
                return 1
        else :
            if orientation == -1:
                return -1
            else :
                return 1
    
    @staticmethod
    def __sortPolarAngle(lowestPoint, coordinates) :
        # Mengurutkan semua koordinat dalam array coordinates berdasarkan polar angle terhadap lowestPoint, memakai algoritma quicksort
        if len(coordinates) == 0 :
            return []
        pivot = coordinates[len(coordinates)//2]
        coordinates.remove(pivot)
        lesser = ConvexHull.__sortPolarAngle(lowestPoint, [x for x in coordinates if ConvexHull.__comparePolarAngle(lowestPoint,x,pivot) < 0])
        greater = ConvexHull.__sortPolarAngle(lowestPoint, [x for x in coordinates if ConvexHull.__comparePolarAngle(lowestPoint,x,pivot) > 0])
        return lesser + [pivot] + greater