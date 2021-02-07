package searcher

import (
	"github.com/EatsLemons/Legacy/apps/backend/storage"
	"github.com/umahmood/haversine"
	"math"
	"sort"
)

type SearchEngine struct {
	store []storage.Culture
}

func NewSearchEngine(store []storage.Culture) *SearchEngine {
	return &SearchEngine{
		store: store,
	}
}

func (se *SearchEngine) SearchClosest(lat float64, lng float64, count int, maxDistance float64) []storage.Culture {
	res := make([]storage.Culture, 0)

	cultureByDistance := make(map[float64]storage.Culture)
	distances := make([]float64, 0, len(se.store))
	for _, reestrCulture := range se.store {
		distance := se.calculateDistance(lat, lng, reestrCulture.Coordinate)
		cultureByDistance[distance] = reestrCulture
		distances = append(distances, distance)
	}

	// it should be optimized
	sort.Float64s(distances)

	for _, d := range distances[:count] {
		m := se.metersTo(lat, lng, cultureByDistance[d].Coordinate)
		if m <= maxDistance {
			res = append(res, cultureByDistance[d])
		}
	}

	return res
}

func (se *SearchEngine) metersTo(lat float64, lng float64, c storage.Coordinate) float64 {
	from := haversine.Coord{Lat: lat, Lon: lng}
	to := haversine.Coord{Lat: c.Latitude, Lon: c.Longitude}

	_, km := haversine.Distance(from, to)

	return km / 1000
}

func (se *SearchEngine) calculateDistance(lat float64, lng float64, c storage.Coordinate) float64 {
	x := math.Abs(lat - c.Latitude)

	y := math.Abs(lng - c.Longitude)
	return x*x + y*y
}
