package storage

type Culture struct {
	Name           string
	CreateDateText string
	PhotoURL       string
	Address        string
	Coordinate     Coordinate
}

type Coordinate struct {
	Latitude  float64
	Longitude float64
}
