#!/bin/bash
echo $WRANGLER_FRAME
echo $WRANGLER_FILE
echo "nuke -x -F $WRANGLER_FRAME $WRANGLER_FILE"
nuke -x -F $WRANGLER_FRAME $WRANGLER_FILE 