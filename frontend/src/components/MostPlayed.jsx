import { useState, useEffect } from 'react';

import More from './More';
import { useApi } from '../contexts/ApiProvider';

export default function MostPlayed({ urlBase, queryParams, renderItem }) {
  const api = useApi();

  const [items, setItems] = useState();
  const [pagination, setPagination] = useState();

  const url = `${urlBase}${queryParams.length > 0 ? '?' + queryParams.join('&') : ''}`;

  useEffect(() => {
    if (!urlBase) return;

    (async () => {
      const response = await api.get(url);
      if (response.ok) {
        setItems(response.body.data);
        setPagination(response.body.pagination);
      } else {
        setItems(null);
      }
    })();
  }, [api, url]);

  const loadNextPage = async () => {
    const nextOffset = pagination.offset + pagination.limit;
    const nextUrl = url.includes('?')
      ? `${url}&offset=${nextOffset}`
      : `${url}?offset=${nextOffset}`;

    const response = await api.get(nextUrl);
    if (response.ok) {
      setItems([...items, ...response.body.data]);
      setPagination(response.body.pagination);
    }
  };

  return (
    <>
      {items === undefined ? (
        <div className="h-full w-full flex justify-center items-center">
          <div className="spinner"></div>
        </div>
      ) : items === null ? (
        <div className="h-full w-full flex justify-center items-center">
          <div>Could not retrieve data</div>
        </div>
      ) : items.length === 0 ? (
          <div className="h-full w-full flex flex-col justify-center items-center bg-primary/25 rounded-xl">
            <svg fill="none" viewBox="0 0 24 24" strokeWidth="1" stroke="currentColor" className="w-12 h-12">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z"/>
            </svg>
            <div className="font-medium text-lg">No {urlBase.replace(/^\//, '').replace(/\/most_played$/, '')}{' '} found</div>
          </div>
      ) : (
          items.map(renderItem)
      )}
      <More pagination={pagination} loadNextPage={loadNextPage}/>

    </>
  );
}