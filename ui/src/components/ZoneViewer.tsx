import useSWR from 'swr';
import { useZone } from '../contexts/ZoneContext';

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function ZoneViewer() {
    const {data: zones, error} = useSWR('/api/zones', fetcher, {refreshInterval: 5000});
    const { currentZone, setCurrentZone } = useZone();

    if (error) return <div>Error loading zones.</div>;
    if (!zones) return <div>Loading zones...</div>;

    const handleZoneClick = (zoneName: string) => {
        setCurrentZone(zoneName);
    };

    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-2">Zones</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {zones.map((zone: any) => (
                    <div 
                        key={zone.id} 
                        className={`bg-gray-100 shadow rounded p-4 cursor-pointer transition-all ${
                            currentZone === zone.name ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-200'
                        }`}
                        onClick={() => handleZoneClick(zone.name)}
                    >
                        <div className="font-semibold">{zone.name}</div>
                        <div>
                            Modifiers: {Array.isArray(zone.modifiers) ? zone.modifiers.join(', ') : String(zone.modifiers) || 'None'}
                        </div>
                        <div>
                            Emotion: <span
                            className={`emotion-badge emotion-${(zone.emotion || 'neutral').toLowerCase()}`}>{zone.emotion || 'Neutral'}</span>
                        </div>
                        {currentZone === zone.name && (
                            <div className="mt-2 text-sm text-blue-600">
                                ✓ Selected
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
