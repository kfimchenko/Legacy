package api

import (
	"encoding/json"
	"github.com/EatsLemons/Legacy/apps/backend/searcher"
	"github.com/EatsLemons/Legacy/apps/backend/storage"
	"net/http"
	"strconv"
)

func FindByCoords(all []storage.Culture, w http.ResponseWriter, req *http.Request) {
	latParam, _ := req.URL.Query()["lat"]
	longParam, _ := req.URL.Query()["long"]
	countParam, _ := req.URL.Query()["count"]
	distanceParam, _ := req.URL.Query()["distance"]

	count := 10
	distance := 5000.0

	lat, _ := strconv.ParseFloat(latParam[0], 64)
	long, _ := strconv.ParseFloat(longParam[0], 64)

	if countParam != nil {
		count, _ = strconv.Atoi(countParam[0])
	}

	if distanceParam != nil {
		distance, _ = strconv.ParseFloat(distanceParam[0], 64)
	}

	cultureObject := findCultureByCoords(all, lat, long, count, distance)
	if len(cultureObject) == 0 {
		w.WriteHeader(http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(cultureObject)
}

type CultureView struct {
	Name           string
	CreateDateText string
	PhotoURL       string
	Address        string
	Distance       int
	Coordinate     storage.Coordinate
}

func makeView(culture storage.Culture, distance int) CultureView {
	return CultureView{
		Name:           culture.Name,
		CreateDateText: culture.CreateDateText,
		PhotoURL:       culture.PhotoURL,
		Address:        culture.Address,
		Distance:       distance,
		Coordinate:     culture.Coordinate,
	}
}

func findCultureByCoords(all []storage.Culture, lat float64, long float64, count int, maxDistance float64) []CultureView {
	s := searcher.NewSearchEngine(all)

	cultures := s.SearchClosest(lat, long, count, maxDistance)

	response := make([]CultureView, 0)

	for _, c := range cultures {
		distance := s.MetersTo(lat, long, c.Coordinate)
		r := makeView(c, int(distance))
		response = append(response, r)
	}

	return response
}

func Truncate3precision(num float64) float64 {
	return float64(int(num*1000)) / 1000
}
