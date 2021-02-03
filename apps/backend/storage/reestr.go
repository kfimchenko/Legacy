package storage

import (
	"bytes"
	"context"
	"encoding/json"
	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
	"io"
)

type ReestrDownloader struct {
	minio *minio.Client
}

func NewReestrDownloader(endpoint string, accessKey string, secretKey string) *ReestrDownloader {
	minioClient, err := minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKey, secretKey, ""),
		Secure: true,
	})

	if err != nil {
		panic(err)
	}

	return &ReestrDownloader{
		minio: minioClient,
	}
}

func (r *ReestrDownloader) Download() []RosReestrCulture {
	var result []RosReestrCulture

	filePaths := r.getReestrFiles()

	for _, filepath := range filePaths {
		object, err := r.minio.GetObject(context.Background(), "legacy", filepath, minio.GetObjectOptions{})
		if err != nil {
			panic(err)
		}

		data := r.streamToByte(object)
		cultures := r.getCultures(data)

		result = append(result, cultures...)
	}

	return result
}

func (r *ReestrDownloader) getReestrFiles() []string {
	return []string{"1.json", "2.json", "3.json", "4.json", "5.json", "6.json", "7.json",
		"8.json", "9.json", "10.json", "11.json", "12.json", "13.json", "14.json", "15.json"}
}

func (r *ReestrDownloader) getCultures(data []byte) []RosReestrCulture {
	var cultures []RosReestrCulture

	err := json.Unmarshal(data, &cultures)
	if err != nil {
		panic(err)
	}

	return cultures
}

func (r *ReestrDownloader) streamToByte(stream io.Reader) []byte {
	buf := new(bytes.Buffer)
	buf.ReadFrom(stream)
	return buf.Bytes()
}

type RosReestrCulture struct {
	NativeId string `json:"nativeId"`
	Data     struct {
		General struct {
			Name       string `json:"name"`
			CreateDate string `json:"createDate"`
			Photo      struct {
				Url string `json:"url"`
			} `json:"photo"`
			Address struct {
				FullAddress string `json:"fullAddress"`
				MapPosition struct {
					Coordinates []float64 `json:"coordinates"`
				} `json:"mapPosition"`
			} `json:"address"`
		} `json:"general"`
	} `json:"data"`
}
