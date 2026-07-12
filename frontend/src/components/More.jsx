export default function More({ pagination, loadNextPage }){
    let thereAreMore = false;
    if(pagination){
        const { offset, count, total } = pagination;
        thereAreMore = offset + count < total;
    }

    return (
        <div className="w-full flex justify-center items-center bg-white">
            {thereAreMore &&
                <button className="px-24 py-1 btn-accent my-2" onClick={loadNextPage}>
                    Load More
                </button>
            }
        </div>
    );
}