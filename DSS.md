# Design Summary Sheet

This document outlines the design and components of the rocket, organized by subteam and section, detailing the contributions of each.

## By Subteam

- **Aero**

  - Nose cone (88cm)
    - COTS 14cm (5.5") diameter, 5.5:1 Von Karman, fibreglass
      - Machined aluminium tip
      - [madcowrocketry - 5.5 nose cone with metal tip](https://www.madcowrocketry.com/fiberglass-5-5-filament-wound-metal-tip-select-shape/)
      - Length of curvature 74cm + length of flat portion 14cm
  - CF Tubes
    - Main chute bay tube (39cm)
    - Airbrakes/drogue chute bay tube (56cm)
    - Engine tube (61cm)
  - Fibreglass tubes
    - Avionics bay tube (33cm)
    - For areas that require RF permeability
  - Aluminum Bulkheads
    - Diameter 13.244cm
    - Thickness 1.5cm
  - Fins
    - Tip to tip attachment
    - Fins made using a composite sandwich:
      - Foam core as the inner base
      - Intermediate layers of glass fibre
      - Outer layers of carbon fibre
    - Specifications:
      - Root chord: 33.1cm
      - Tip chord: 13.95cm
      - Span: 13.5cm
      - Sweep angle: 35.35 degrees

- **Airbrakes**

  - Airbrakes flaps cut from body tube
    - 3 flaps extending radially
    - Flaps mounted on PETG supports with fore edge on a hinge and the aft edge connected to PETG push rod
    - Lead screw driven by DC motor actuates push rods
    - DC motor with gearbox operated using custom flight controller powered by 18650 Li-ion cells

- **Avionics**

  - Dual deployment with redundant electronics
    - Primary: Featherweight Blue Raven + Featherweight GPS
    - Redundant: Altus Metrum Telemega (integrated GPS)
  - Two-sided "sled" style avionics bay made of polycarbonate sheets and 3D printed PETG parts

- **Payload**

  - 3U Payload
    - 9.6cm x 9.6cm x 30cm
      - Needs to be undersized from 10cm profile to fit existing nosecone
    - CubeSat form factor frame made from aluminium
    - Contains the SRAD flight computer
    - Ballast to reach target mass (inert, possibly a pioreactor)
    - 4000g (8.818lbs) (subject to change)

- **Propulsion**

  - 3G 96mm CTI hardware
    - M2505 as chosen reload
      - Performance: Total impulse of 7450.00 N·s, average thrust of 2491.02 N, and maximum thrust of 2952.61 N over a 3.00-second burn time
      - Specifications: Dimensions of 98.0 mm x 579.0 mm, with a propellant mass of 3.339 kg and casing mass of 2.866 kg
      - Ignition System: Dual-headed boron igniter
    - Alternatives: M1290, M1520

- **Recovery**
  - Main chute
    - 244cm (96") ripstop nylon main chute
      - Six 30cm shroud lines
  - Drogue chute
    - 61cm (24") ripstop nylon drogue chute
      - Six 30cm shroud lines
  - Kevlar shock cords

## By Section

- **Nose cone (88cm)**

  - COTS 14cm (5.5") diameter, 5.5:1 Von Karman, fibreglass
    - Machined aluminium tip
    - [madcowrocketry - 5.5 nose cone with metal tip](https://www.madcowrocketry.com/fiberglass-5-5-filament-wound-metal-tip-select-shape/)
    - Length of curvature 74cm + length of flat portion 14cm
  - 3U Payload
    - 9.6cm x 9.6cm x 30cm
    - CubeSat form factor frame made from aluminium
    - Contains SRAD flight computer and ballast
    - 4000g (8.818lbs)
  - Aluminum Bulkhead
    - Diameter 13.244cm
    - Thickness 1.5cm

- **Main chute bay (39cm)**

  - Carbon fibre tube
  - 244cm (96") ripstop nylon main chute
    - Six 30cm shroud lines

- **Avionics bay (33cm)**

  - Fibreglass tube (chosen over CF for RF permeability)
  - Dual deployment with redundant electronics
    - Primary: Featherweight Blue Raven + Featherweight GPS
    - Redundant: Altus Metrum Telemega (integrated GPS)

- **Airbrakes - drogue chute bay (56cm)**

  - Carbon fibre tube
  - 61cm (24") ripstop nylon drogue chute
    - Six 30cm shroud lines
  - Airbrakes flaps cut from body tube
    - 3 flaps extending radially
    - Flaps mounted on PETG supports with fore edge on a hinge and the aft edge connected to PETG push rod
    - Lead screw driven by DC motor actuates push rods
    - DC motor operated using custom flight controller powered by 18650 Li-ion cells

- **Engine tube (61cm)**
  - Carbon fibre tube
  - 3G 96mm CTI hardware
    - M2505 as chosen reload
      - Performance: Total impulse of 7450.00 N·s, average thrust of 2491.02 N, and maximum thrust of 2952.61 N over a 3.00-second burn time
      - Specifications: Dimensions of 98.0 mm x 579.0 mm, with a propellant mass of 3.339 kg and casing mass of 2.866 kg
      - Ignition System: Dual-headed boron igniter
      - Alternatives: M1290, M1520
  - Tip to tip attachment of fins
    - Fins made using a composite sandwich consisting of foam core as the inner base followed by intermediate layers of glass fibre followed by outer layers of carbon fibre
    - Specifications: Root chord of 33.1cm, tip chord of 13.95cm, span of 13.5cm, and sweep angle of 35.35 degrees
