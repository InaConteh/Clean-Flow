export type WaterStatus = "green" | "yellow" | "red";

export interface WaterSourceProperties {
  id: string;
  name: string;
  status: WaterStatus;
  last_tested: string | null;
  district: string | null;
}

export interface GeoJSONFeature {
  type: "Feature";
  geometry: { type: "Point"; coordinates: [number, number] };
  properties: WaterSourceProperties;
}

export interface GeoJSONCollection {
  type: "FeatureCollection";
  features: GeoJSONFeature[];
}

export interface Tip {
  id: number;
  title: string;
  body: string;
  icon: string;
}
