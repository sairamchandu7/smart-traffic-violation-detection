# B.Tech Prototype Notes

This project is now configured as a prototype that uses a recorded traffic video by default instead of a live CCTV feed.

## Demo modes

- `config.yaml`: recorded video prototype mode
- `config.live.yaml`: live camera mode for later testing
- `config.overspeed-demo.yaml`: recorded video demo with a low speed limit so overspeed cases appear more easily during presentation

## Current prototype behavior

- reads a saved traffic video
- shows tracked vehicles with IDs
- estimates speed between two configured road lines
- highlights overspeed cases
- stores violation evidence in `data/violations`
- displays a cleaner dashboard for project presentation

## Important accuracy note

For true `no helmet` detection and accurate number plate extraction, you still need:

- a recorded video that clearly contains helmet violations
- a trained helmet / no-helmet model
- a trained number plate detector
- correct road calibration for the speed zone

The current default setup is presentation-friendly, but final accuracy depends on the models and the chosen demo video.

## Demo tip

If you want to guarantee overspeed alerts during a classroom presentation, run the project with `config.overspeed-demo.yaml`. This uses the same recorded traffic video but applies a lower speed limit only for prototype testing.
