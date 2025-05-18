import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function ZoneViewer() {
    const {data: zones, error} = useSWR('/api/zones', fetcher, {refreshInterval: 5000});

    if (error) return <div>Error loading zones.</div>;
    if (!zones) return <div>Loading zones...</div>;

    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-2">Zones</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {zones.map((zone: any) => (
                    <div key={zone.id} className="bg-gray-100 shadow rounded p-4">
                        <div className="font-semibold">{zone.name}</div>
                        <div>
                            Modifiers: {zone.modifiers?.join(', ') || 'None'}
                        </div>
                        <div>
                            Emotion: <span
                            className={`emotion-badge emotion-${(zone.emotion || 'neutral').toLowerCase()}`}>{zone.emotion || 'Neutral'}</span>
                        </div>
                        {/* Add overlays, assets, etc as needed */}
                    </div>
                ))}
            </div>
        </div>
    );
}