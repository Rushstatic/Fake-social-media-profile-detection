import { useCallback } from 'react';
import Particles from 'react-tsparticles';
import { loadSlim } from "tsparticles-slim";


export default function ParticlesBackground({ color = "#7f5af0" }) {
const init = useCallback(async (engine) => {
  await loadSlim(engine);
}, []);


  return (
    <Particles
      id="tsparticles"
      init={init}
      options={{
        fullScreen: { enable: false },
        background: { color: { value: 'transparent' } },
particles: {
  number: {
    value: 120, // Dense but elegant
    density: { enable: true, area: 800 }
  },
  size: {
    value: { min: 1, max: 2.5 },
    random: true
  },
  opacity: {
    value: 0.85,
    animation: {
      enable: true,
      speed: 0.5,
      minimumValue: 0.3,
      sync: false
    }
  },
  move: {
    enable: true,
    speed: 0.25,
    direction: "none",
    random: false,
    straight: false,
    outModes: { default: "bounce" }
  },
  color: { value: color,
  animation: {
    enable: true,
    speed: 5,
    sync: false
  } },
  shape: { type: "circle" }
},
interactivity: {
  events: {
    onHover: { enable: true, mode: "repulse" },
    onClick: { enable: true, mode: "push" }
  },
  modes: {
    repulse: {
      distance: 80,
      duration: 0.4
    },
    push: {
      quantity: 4
    }
  }
}


      }}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0
      }
    }
      
    />
  );
}
