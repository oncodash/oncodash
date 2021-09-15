
export async function get(url: string) {

    const response = await fetch(url)
    const json = await response.json()

    return json

}

export async function post(url: string, data: any) {
    const opts = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }

    const response = await fetch(url, opts)
    const json = await response.json()

    return json

}