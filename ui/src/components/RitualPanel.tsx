import useSWR from 'swr';

const TOKEN = import.meta.env.VITE_ETERNA_TOKEN;

const fetcher = (url: string) => fetch(url, {
    headers: {
        "Authorization": `Bearer ${TOKEN}`
    }
}).then(res => res.json());

export default function RitualPanel() {
    const {data: rituals, error, mutate} = useSWR('/api/rituals', fetcher, {refreshInterval: 5000});

    const triggerRitual = async (id: string) => {
        await fetch(`/api/rituals/trigger/${id}`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${TOKEN}`
            }
        });
        mutate(); // Revalidate rituals after triggering
    };

    if (error) return <div>Error loading rituals.</div>;
    if (!rituals) return <div>Loading rituals...</div>;

    return (
        <div className="p-4">
            <h3 className="text-xl font-bold mb-2">Available Rituals</h3>
            <ul>
                {rituals.map((ritual: any) => (
                    <li key={ritual.id} className="flex items-center mb-2">
                        <span className="flex-1">{ritual.name}</span>
                        <button
                            onClick={() => triggerRitual(ritual.id)}
                            className="ml-2 px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                        >
                            Trigger
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
