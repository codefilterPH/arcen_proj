class FilterSortPaginate:

    @staticmethod
    def filter_sort_paginate(request, records, order_fields):
        # Search term
        search_term = request.GET.get('search[value]', None)

        # Filter based on search term
        if search_term:
            records = [
                data for data in records if
                any(search_term.lower() in str(value).lower() for value in data.values() if value)
            ]

        # Order by
        order_column = request.GET.get('order[0][column]', 0)
        order_dir = request.GET.get('order[0][dir]', 'asc')

        # Ensure the order column index is within range
        order_column_index = int(order_column) if str(order_column).isdigit() and int(order_column) < len(
            order_fields) else 0
        order_field = order_fields[order_column_index]

        # Sort the data
        records = sorted(
            records,
            key=lambda x: x[order_field] if isinstance(x, dict) else '',
            reverse=(order_dir == 'desc')
        )

        # Pagination: Page and page length
        start = int(request.GET.get('start', 0))
        length = request.GET.get('length', None)  # Allow for showing all

        # If length is None or -1, show all entries
        if length is None or int(length) == -1:
            paginated_data = records
        else:
            length = int(length)
            end = start + length
            paginated_data = records[start:end]

        return paginated_data, len(records)
