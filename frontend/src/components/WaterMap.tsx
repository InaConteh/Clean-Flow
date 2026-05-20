import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { GeoJSONFeature, WaterStatus } from "../types";
import StatusBadge from "./StatusBadge";

const markerColors: Record<WaterStatus, string> = {
  green: "#28a745",
  yellow: "#ffc107",
  red: "#dc3545",
};

interface Props {
  features: GeoJSONFeature[];
}

export default function WaterMap({ features }: Props) {
  const center: [number, number] = features.length
    ? [
        features.reduce((s, f) => s + f.geometry.coordinates[1], 0) /
          features.length,
        features.reduce((s, f) => s + f.geometry.coordinates[0], 0) /
          features.length,
      ]
    : [8.5, -11.5];

  return (
    <MapContainer
      center={center}
      zoom={7}
      scrollWheelZoom
      className="leaflet-container"
      aria-label="Water sources map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {features.map((f) => {
        const [lng, lat] = f.geometry.coordinates;
        const { id, name, status, district } = f.properties;
        return (
          <CircleMarker
            key={id}
            center={[lat, lng]}
            radius={10}
            pathOptions={{
              color: markerColors[status],
              fillColor: markerColors[status],
              fillOpacity: 0.85,
            }}
          >
            <Popup>
              <div className="min-w-[180px]">
                <p className="font-bold text-primary">{name}</p>
                <StatusBadge status={status} />
                {district && (
                  <p className="mt-1 text-xs text-neutral">{district}</p>
                )}
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}
