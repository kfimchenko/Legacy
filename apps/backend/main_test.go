package main

import "testing"

func TestTruncate(t *testing.T) {
	v := 1.1119
	res := Truncate3precision(v)
	if res != 1.111 {
		t.Errorf("result shoud be 1.111 but it's %v", v)
	}
}
