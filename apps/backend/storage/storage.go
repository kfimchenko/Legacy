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

func TryMapFromRosReestr(rc RosReestrCulture) (Culture, bool) {
	if len(rc.Data.General.Address.MapPosition.Coordinates) < 2 {
		return Culture{}, false
	}

	return Culture{
		Name:           rc.Data.General.Name,
		CreateDateText: rc.Data.General.CreateDate,
		PhotoURL:       rc.Data.General.Photo.Url,
		Address:        rc.Data.General.Address.FullAddress,
		Coordinate: Coordinate{
			Latitude:  rc.Data.General.Address.MapPosition.Coordinates[1],
			Longitude: rc.Data.General.Address.MapPosition.Coordinates[0],
		},
	}, true
}
