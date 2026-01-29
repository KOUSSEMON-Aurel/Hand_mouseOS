package main

import "C"
import (
	"math"
	"unsafe"
)

//export GoDistance3D
func GoDistance3D(x1, y1, z1, x2, y2, z2 float32) float32 {
	dx := x1 - x2
	dy := y1 - y2
	dz := z1 - z2
	return float32(math.Sqrt(float64(dx*dx + dy*dy + dz*dz)))
}

//export GoBatchDistances
func GoBatchDistances(p1s_ptr *float32, p2s_ptr *float32, results_ptr *float32, n int) {
	p1s := (*[1 << 30]float32)(unsafe.Pointer(p1s_ptr))[:n*3 : n*3]
	p2s := (*[1 << 30]float32)(unsafe.Pointer(p2s_ptr))[:n*3 : n*3]
	results := (*[1 << 30]float32)(unsafe.Pointer(results_ptr))[:n : n]

	for i := 0; i < n; i++ {
		dx := p1s[i*3] - p2s[i*3]
		dy := p1s[i*3+1] - p2s[i*3+1]
		dz := p1s[i*3+2] - p2s[i*3+2]
		results[i] = float32(math.Sqrt(float64(dx*dx + dy*dy + dz*dz)))
	}
}

func main() {}
