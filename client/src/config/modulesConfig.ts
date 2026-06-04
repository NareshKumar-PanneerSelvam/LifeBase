import React from 'react';
import { Cpu } from 'lucide-react';
import OverviewModule from '../components/modules/OverviewModule';

export interface ModuleConfig {
  id: string;
  name: string;
  route: string; // Nesting path (e.g., 'logs' or '' for overview index)
  icon: React.ComponentType<any>; // Lucide react icon reference
  component: React.ComponentType<any>; // Component class/function to render
  description: string;
}

// Simply add new module config objects to this array to automatically register their route and sidebar icon.
export const modulesConfig: ModuleConfig[] = [
  {
    id: 'overview',
    name: 'System Overview',
    route: '', // Root dashboard view (index route)
    icon: Cpu,
    component: OverviewModule,
    description: 'LifeBase system vitals and server health check.'
  }
];
