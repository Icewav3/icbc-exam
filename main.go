package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

const (
	loginURL        = "https://onlinebusiness.icbc.com/deas-api/v1/webLogin/webLogin"
	appointmentsURL = "https://onlinebusiness.icbc.com/deas-api/v1/web/getAvailableAppointments"
)

type Login struct {
	LastName      string `json:"drvrLastName"`
	LicenceNumber string `json:"licenceNumber"`
	Keyword       string `json:"keyword,omitempty"`
}

type Config struct {
	LastName      string `json:"LastName"`
	LicenceNumber string `json:"LicenceNumber"`
	Keyword       string `json:"Keyword"`
}

func loadConfig(configPath string) Config {
	var config Config
	var configFile, err = os.Open(configPath)
	defer configFile.Close()

	if err != nil {
		panic(err)
	}
	jsonParser := json.NewDecoder(configFile)
	jsonParser.Decode(&config)
	return config
}

func login(LastName, LicenceNumber, Keyword string) string {
	login := Login{
		LastName:      LastName,
		LicenceNumber: LicenceNumber,
		Keyword:       Keyword,
	}
	client := &http.Client{}

	loginJson, err := json.Marshal(login)
	if err != nil {
		panic(err)
	}

	req, err := http.NewRequest(http.MethodPut, loginURL, bytes.NewBuffer(loginJson))
	if err != nil {
		panic(err)
	}
	req.Header.Set("Content-type", "application/json")
	req.Header.Set("Accept", "application/json, text/plain, */*")
	req.Header.Set("Referer", "https://onlinebusiness.icbc.com/webdeas-ui/login;type=driver")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")

	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	if resp.StatusCode == 200 {
		return resp.Header.Get("Authorization")
	} else {
		return ""
	}
}
func main() {
	conf := loadConfig("config.json")

	token := login(conf.LastName, conf.LicenceNumber, conf.Keyword)
	if token != "" {
		fmt.Println("Get appointments")
	} else {
		fmt.Println("Auth error")
	}
}
