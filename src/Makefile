CC      = gcc
LDFLAGS = -ldl
CFLAGS  = -shared -fPIC -O2 -s -W -Wall
TARGET  = hook.so
SRC     = hook.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
	rm -f $(TARGET)

.PHONY: all clean

