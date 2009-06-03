
.PHONY: clean java python

all: cpp java python lastfm.jar

PROTOC = /home/speed/tmacam/tmp/protobuf-2.0.3/bin/protoc
JAVA_EXTRA_CLASSPATH = ./protobuf-java-2.0.3.jar
CLASSPATH=$(JAVA_EXTRA_CLASSPATH)

protoc_middleman: lastfm.proto
	$(PROTOC) --cpp_out=. --java_out=. --python_out=. lastfm.proto
	#$(PROTOC) --java_out=. --python_out=. lastfm.proto
	@touch protoc_middleman

python: protoc_middleman

java: protoc_middleman
	CLASSPATH=$(CLASSPATH) javac lastfm/Lastfm.java

cpp: protoc_middleman

snapshot_proto: library_snap.proto
	$(PROTOC) --python_out=. library_snap.proto
	@touch snapshot_proto

lastfm.jar: java
	jar cvf $@ lastfm/

clean:
	@rm -fv protoc_middleman
	@rm -rfv lastfm
	@rm -fv lastfm_pb2.py
	@rm -fv lastfm.jar
