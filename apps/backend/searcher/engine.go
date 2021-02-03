package searcher

import (
	"github.com/EatsLemons/Legacy/apps/backend/storage"
)

type SearchEngine struct {
	store []storage.RosReestrCulture
}

func NewSearchEngine(store []storage.RosReestrCulture) *SearchEngine {
	return &SearchEngine{
		store: store,
	}
}

func (se *SearchEngine) SearchClosest(lat float64, lng float64) storage.RosReestrCulture {
	closet := se.store[0]

	return closet
}
